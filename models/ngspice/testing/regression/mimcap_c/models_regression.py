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

from docopt import docopt
import pandas as pd
import numpy as np
import os
from jinja2 import Template
import concurrent.futures
import shutil
import multiprocessing as mp
import logging
from subprocess import Popen, PIPE
import glob

# CONSTANT VALUES
DEFAULT_TEMP = 25.0
PASS_THRESH = 5.0


def find_mimcap(filename):
    """
    Find mimcap in log
    """

    """
    This function extracts cap value for each run from log files.
    Parameters
    ----------
    filename : string or Path
        Path string to the location of the log output file.

    Returns
    -------
    float
        A float value for cap simulated for each log.
    """

    with open(filename) as log:
        log_data = log.readlines()

    cap_val = 0
    for line in log_data:
        if "cv" in line:
            cap_val = float(line.split("=")[1])

    return cap_val


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    return os.system(f"ngspice -b -a {file_name} -o {file_name}.log > {file_name}.log")


def ext_measured(dev_data_path, device):
    # Read Data
    df = pd.read_excel(dev_data_path)
    loops = df["CV (fF)"].count()
    dev_count = 3
    sizes_count = 4
    temp_count = dev_count * sizes_count
    corner_count = dev_count * temp_count

    idf = df[["CV (fF)"]].copy()
    idf.rename(
        columns={"CV (fF)": "mimcap_measured"}, inplace=True,
    )
    idf["length"] = df["Unnamed: 2"].apply(
        lambda x: str(x).split("(")[1].split("x")[0].split("u")[0]
    )
    idf["width"] = df["Unnamed: 2"].apply(
        lambda x: str(x).split("(")[1].split("x")[1].split("u")[0]
    )

    # Get device names from measured data
    idf["device"] = df["Unnamed: 2"].apply(
        lambda x: str(x).split("(")[0].replace("\n", "")
    )

    # Renaming mim devices with its new names
    idf["device"] = idf["device"].apply(
        lambda x: str(x).replace("mim_1p5fF", "cap_mim_1f5")
    )
    idf["device"] = idf["device"].apply(
        lambda x: str(x).replace("mim_1p0fF", "cap_mim_1f0")
    )
    idf["device"] = idf["device"].apply(
        lambda x: str(x).replace("mim_2p0fF", "cap_mim_2f0")
    )

    # Adding mim varaints depending on stack option [mim-A , mim-B]
    # MIM-A is allowed only for M2-M3
    # MIM-B is allowed for M3-M4 , M4-M5 , M5-M6
    idf["device"] = idf["device"].apply(lambda x: f"{str(x)}_{device}")

    corners = []
    temps = []
    for i in range(0, loops):
        # Corner & temp selection based on measured data
        if i in range(0, corner_count):
            corner = "ss"
            if i in range(0, temp_count):
                temp = 25
            elif i in range(temp_count, 2 * temp_count):
                temp = -40
            else:
                temp = 175
        elif i in range(corner_count, 2 * corner_count):
            corner = "typical"
            if i in range(corner_count, corner_count + temp_count):
                temp = 25
            elif i in range(corner_count + temp_count, corner_count + 2 * temp_count):
                temp = -40
            else:
                temp = 175
        elif i in range(2 * corner_count, 3 * corner_count):
            corner = "ff"
            if i in range(2 * corner_count, 2 * corner_count + temp_count):
                temp = 25
            elif i in range(
                2 * corner_count + temp_count, 2 * corner_count + 2 * temp_count
            ):
                temp = -40
            else:
                temp = 175
        else:
            corner = "typical"  # Default
            temp = 25  # Default

        corners.append(corner)
        temps.append(temp)

    idf["corner"] = corners
    idf["temp"] = temps

    idf.dropna(axis=0, inplace=True)
    idf.drop_duplicates(inplace=True)
    idf = idf[["device", "corner", "length", "width", "temp", "mimcap_measured"]]
    return idf


def run_sim(dirpath, device, length, width, corner, temp):
    """Run simulation at specific information and corner"""
    netlist_tmp = "./device_netlists/mimcap.spice"

    info = {}
    info["device"] = device
    info["corner"] = corner
    info["temp"] = temp
    info["width"] = width
    info["length"] = length

    netlist_path = (
        f"{dirpath}/{device}_netlists/netlist_w{width}_l{length}_t{temp}_{corner}.spice"
    )

    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        os.makedirs(f"{dirpath}/{device}_netlists", exist_ok=True)

        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device, width=width, length=length, corner=corner, temp=temp,
                )
            )

    # Running ngspice for each netlist
    try:
        call_simulator(netlist_path)
        # Find mimcap in log
        try:
            mim = find_mimcap(f"{netlist_path}.log")

        except Exception as exec:
            mim = 0.0
            print(exec)

    except Exception:
        mim = 0.0

    info["mim_sim"] = mim

    return info


def run_sims(df, dirpath, num_workers=mp.cpu_count()):

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
    df = df[["device", "corner", "length", "width", "temp", "mim_sim"]]

    return df


def main():
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
                "ngspice version is not supported. Please use ngspice version 38 or newer."
            )
            exit(1)

    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    main_regr_dir = "mimcap_regr"

    devices = [
        "m2m3_noshield",
        "m3m4_noshield",
        "m4m5_noshield",
        "m5m6_noshield",
    ]

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(f"{dev_path}", exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {dev}")

        mim_data_files = glob.glob("../../180MCU_SPICE_DATA/Cap/mimcap_fc.nl_out.xlsx")
        if len(mim_data_files) < 1:
            logging.info(f"# Can't find mimcap file for device: {dev}")
            mim_file = ""
        else:
            mim_file = os.path.abspath(mim_data_files[0])
        logging.info(f"# mimcap data points file : {mim_file}")

        if mim_file == "":
            logging.info(f"# No datapoints available for validation for device {dev}")
            continue

        if mim_file != "":
            meas_df = ext_measured(mim_file, dev)
        else:
            meas_df = []

        logging.info(
            f"# Device MIM {dev} number of measured_datapoints : {len(meas_df)}"
        )

        sim_df = run_sims(meas_df, dev_path, workers_count)
        logging.info(
            f"# Device MIM {dev} number of simulated datapoints :{len(sim_df)}"
        )

        merged_df = meas_df.merge(
            sim_df, on=["device", "corner", "length", "width", "temp"], how="left"
        )
        merged_df["error"] = (
            np.abs(merged_df["mim_sim"] - merged_df["mimcap_measured"])
            * 100.0
            / merged_df["mimcap_measured"]
        )
        meas_df.to_csv(f"{dev_path}/meas_df.csv", index=False)
        sim_df.to_csv(f"{dev_path}/sim_df.csv", index=False)
        merged_df.drop_duplicates(inplace=True)
        merged_df.to_csv(f"{dev_path}/error_analysis.csv", index=False)
        m1 = merged_df["error"].min()
        m2 = merged_df["error"].max()
        m3 = merged_df["error"].mean()
        logging.info(
            f"# Device MIM {dev} min error: {m1:.2f} , max error: {m2:.2f}, mean error {m3:.2f}"
        )

        # Verify regression results
        if merged_df["error"].max() < PASS_THRESH:
            logging.info(f"# Device {dev} has passed regression.")
        else:
            logging.error(
                f"# Device {dev} has failed regression. Needs more analysis."
            )
            logging.error(
                "#Failed regression for MIMCAP analysis."
            )
            exit(1)

# ================================================================
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
        handlers=[logging.StreamHandler()],
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Calling main function
    main()
