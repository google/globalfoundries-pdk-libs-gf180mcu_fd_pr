# Copyright 2022 GlobalFoundries PDK Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Usage:
  models_regression.py [--num_cores=<num>]

  -h, --help             Show help text.
  -v, --version          Show version.
  --num_cores=<num>      Number of cores to be used by simulator
"""

from unittest.mock import DEFAULT
from docopt import docopt
import pandas as pd
import numpy as np
import os
from jinja2 import Template
import concurrent.futures
import shutil
import multiprocessing as mp
import logging
import subprocess
import glob

DEFAULT_TEMP = 25.0
PASS_THRESH = 2.0


def find_moscap(filename):
    """
    Find moscap in log
    """
    cmd = 'grep "cv" {} | head -n 1'.format(filename)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return float(process.communicate()[0][:-1].decode("utf-8").split("=")[1])


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    return os.system(f"ngspice -b -a {file_name} -o {file_name}.log > {file_name}.log")


def ext_measured(dev_data_path: str, device: str, corners: str) -> pd.DataFrame:
    """Extract measured data from excel file
    Args:
        dev_data_path (str): Path to excel file
        device (str): Device type
        corners (str): Corner type
    Returns:
        pd.DataFrame: Measured data
    """
    # Read Data
    df = pd.read_excel(dev_data_path)

    length = []
    width = []
    corner = []
    moscap_meas = []

    for i in range(len(df)):

        a_str = df["Unnamed: 2"][i]  # area_string parameter
        moscap_corners = df["corners"][i]
        moscap_val = df["CV (fF)"][i]

        if ("nmos" in str(a_str)) and ("nmos" in device):

            if ("b" in str(a_str)) and ("b" in device):

                length.append(float(a_str.split("(")[1].split("x")[0].split("u")[0]))
                width.append(float(a_str.split("(")[1].split("x")[1].split("u")[0]))
                moscap_meas.append(float(moscap_val))

                if type(moscap_corners) == str:

                    corner.append((moscap_corners.split("_")[-1]))

                else:
                    corner.append(moscap_corners)

            elif ("b" not in str(a_str)) and ("b" not in device):

                length.append(float(a_str.split("(")[1].split("x")[0].split("u")[0]))
                width.append(float(a_str.split("(")[1].split("x")[1].split("u")[0]))
                moscap_meas.append(float(moscap_val))

                if type(moscap_corners) == str:

                    corner.append((moscap_corners.split("_")[-1]))

                else:
                    corner.append(moscap_corners)

        if ("pmos" in str(a_str)) and ("pmos" in device):

            if ("b" in str(a_str)) and ("b" in device):

                length.append(float(a_str.split("(")[1].split("x")[0].split("u")[0]))
                width.append(float(a_str.split("(")[1].split("x")[1].split("u")[0]))
                moscap_meas.append(float(moscap_val))

                if type(moscap_corners) == str:

                    corner.append((moscap_corners.split("_")[-1]))

                else:
                    corner.append(moscap_corners)

            elif ("b" not in str(a_str)) and ("b" not in device):
                length.append(float(a_str.split("(")[1].split("x")[0].split("u")[0]))
                width.append(float(a_str.split("(")[1].split("x")[1].split("u")[0]))
                moscap_meas.append(float(moscap_val))

                if type(moscap_corners) == str:

                    corner.append((moscap_corners.split("_")[-1]))

                else:
                    corner.append(moscap_corners)

    idf = {}

    idf["length"] = length
    idf["width"] = width
    idf["corner"] = corner
    idf["moscap_measured"] = moscap_meas

    df = pd.DataFrame(idf)
    df["temp"] = DEFAULT_TEMP
    df["device"] = device
    df.dropna(axis=0, inplace=True)
    df.drop_duplicates(inplace=True)
    df = df[["device", "corner", "length", "width", "temp", "moscap_measured"]]

    return df


def run_sim(
    dirpath: str, device: str, length: float, width: float, corner: str, temp=25
) -> dict:
    """Run simulation for a given device, corner, length, width and temperature
    Args:
        dirpath (str): Path to directory
        device (str): Device type
        length (float): Device length
        width (float): Device width
        corner (str): Corner type
        temp (float, optional): Device temperature. Defaults to 25.
    Returns:
        dict: Simulation results
    """
    netlist_tmp = "./device_netlists/moscap.spice"

    info = {}
    info["device"] = device
    info["corner"] = corner
    info["temp"] = temp
    info["width"] = width
    info["length"] = length

    width_str = "{:.1f}".format(width)
    length_str = "{:.1f}".format(length)
    temp_str = "{:.1f}".format(temp)

    netlist_path = f"{dirpath}/{device}_netlists/netlist_w{width_str}_l{length_str}_t{temp_str}_{corner}.spice"

    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        os.makedirs(f"{dirpath}/{device}_netlists", exist_ok=True)

        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device,
                    width=width_str,
                    length=length_str,
                    corner=corner,
                    temp=temp_str,
                )
            )

    # Running ngspice for each netlist
    try:
        call_simulator(netlist_path)
        # Find moscap in log
        try:
            moscap = find_moscap(f"{netlist_path}.log")

        except Exception:
            moscap = 0.0

    except Exception:
        moscap = 0.0

    # logging.info(moscap)

    info["moscap_sim_unscaled"] = moscap

    return info


def run_sims(
    df: pd.DataFrame, dirpath: str, num_workers=mp.cpu_count()
) -> pd.DataFrame:
    """Run simulations for a given dataframe
    Args:
        df (pd.DataFrame): Dataframe containing device, corner, length, width and temperature
        dirpath (str): Path to directory
        num_workers (int, optional): Number of workers. Defaults to mp.cpu_count().
    Returns:
        pd.DataFrame: Dataframe containing simulation results
    """

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures_list = []
        for j, row in df.iterrows():
            futures_list.append(
                executor.submit(
                    run_sim,
                    dirpath,
                    row["device"],
                    row["length"],
                    row["width"],
                    row["corner"],
                    row["temp"],
                )
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logging.info(f"Test case generated an exception: {exc}")

    df = pd.DataFrame(results)
    df = df[["device", "corner", "length", "width", "temp", "moscap_sim_unscaled"]]

    df["moscap_sim"] = df["moscap_sim_unscaled"]
    return df


def main():
    """Main function for moscap regression"""
    # ======= Checking ngspice  =======
    ngspice_v_ = os.popen("ngspice -v").read()

    if "ngspice-" not in ngspice_v_:
        logging.error("ngspice is not found. Please make sure ngspice is installed.")
        exit(1)
    else:
        version = int((ngspice_v_.split("\n")[1]).split(" ")[1].split("-")[1])
        print(version)
        if version <= 37:
            logging.error(
                "ngspice version is not supported. Please use ngspice version 38 or newer or newer."
            )
            exit(1)

    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    main_regr_dir = "moscap_regr"

    # moscap var.
    corners = ["typical", "ff", "ss"]

    devices = [
        "cap_nmos_03v3",
        "cap_pmos_03v3",
        "cap_nmos_03v3_b",
        "cap_pmos_03v3_b",
        "cap_nmos_06v0",
        "cap_pmos_06v0",
        "cap_nmos_06v0_b",
        "cap_pmos_06v0_b",
    ]

    # devices = [devices_3p3, devices_6p0]

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(f"{dev_path}", exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {dev}")

        if "3v3" in dev:
            dev_ind = "3p3"
        else:
            dev_ind = "6p0"

        moscap3p3_data_files = glob.glob(
            f"../../180MCU_SPICE_DATA/Cap/moscap_cv_{dev_ind}.nl_out.xlsx"
        )
        if len(moscap3p3_data_files) < 1:
            logging.error(f"# Can't find moscap_3p3 file for device: {dev}")
            moscap3p3_file = ""
        else:
            moscap3p3_file = os.path.abspath(moscap3p3_data_files[0])
        logging.info(f"# moscap_3p3 data points file : {moscap3p3_file}")

        if moscap3p3_file == "":
            logging.error(f"# No datapoints available for validation for device {dev}")
            continue

        if moscap3p3_file != "":
            meas_df = ext_measured(moscap3p3_file, dev, corners)
        else:
            meas_df = []

        logging.info(f"# Device {dev} number of measured_datapoints : {len(meas_df)}")

        sim_df = run_sims(meas_df, dev_path, 3)
        logging.info(f"# Device {dev} number of simulated datapoints : {len(sim_df)}")

        merged_df = meas_df.merge(
            sim_df, on=["device", "corner", "length", "width", "temp"], how="left"
        )

        merged_df["error"] = (
            np.abs(merged_df["moscap_sim"] - merged_df["moscap_measured"])
            * 100.0
            / merged_df["moscap_measured"]
        )

        merged_df.to_csv(f"{dev_path}/error_analysis.csv", index=False)

        m1 = merged_df["error"].min()
        m2 = merged_df["error"].max()
        m3 = merged_df["error"].mean()

        logging.info(
            f"# Device {dev} min error: {m1:.2f} , max error: {m2:.2f}, mean error {m3:.2f}"
        )

        if merged_df["error"].max() < PASS_THRESH:
            logging.info(f"# Device {dev} has passed regression.")
        else:
            logging.error(f"# Device {dev} has failed regression. Needs more analysis.")


# # ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================

if __name__ == "__main__":

    # Args
    arguments = docopt(__doc__, version="comparator: 0.1")
    workers_count = (
        os.cpu_count() * 2
        if arguments["--num_cores"] is None
        else int(arguments["--num_cores"])
    )
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            logging.StreamHandler(),
        ],
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Calling main function
    main()
