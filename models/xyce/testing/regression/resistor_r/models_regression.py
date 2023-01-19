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

import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

PASS_THRESH = 2.0
DEFAULT_TEMP = 25.0
DEFAULT_VOLTAGE = 1.0


def find_res(filename):
    """
    Find res in log
    """
    cmd = 'grep " R  " {} | tail -n 1'.format(filename)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    x = process.communicate()[0][:-1].decode("utf-8")
    # split the line into a list
    x = x.split(" ")
    # remove empty strings
    x = list(filter(None, x))
    # return the 1rd element
    return float(x[1])


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    log_file = file_name.replace("-hspice-ext all ", "")
    os.system(f"Xyce {file_name} -l {log_file}.log 2> /dev/null")


def ext_const_temp_corners(
    dev_data_path: str, device: str, corners: str
) -> pd.DataFrame:
    """Extract constant temperature corners from excel file.
    Args:
        dev_data_path (str): Path to excel file.
        device (str): Device name.
        corners (str): Corner names.
    Returns:
        pd.DataFrame: Dataframe with extracted data.
    """
    # Read Data
    df = pd.read_excel(dev_data_path)

    all_dfs = []
    for corner in corners:
        idf = df[["l (um)", "w (um)", f"res_{corner} Rev9 "]].copy()
        idf.rename(
            columns={
                f"res_{corner} Rev9 ": "res_measured",
                "l (um)": "length",
                "w (um)": "width",
            },
            inplace=True,
        )
        idf["corner"] = corner
        all_dfs.append(idf)

    df = pd.concat(all_dfs)
    df["temp"] = DEFAULT_TEMP
    df["device"] = device
    df["voltage"] = DEFAULT_VOLTAGE
    df.dropna(axis=0, inplace=True)
    df = df[["device", "corner", "length", "width", "voltage", "temp", "res_measured"]]
    df.drop_duplicates(inplace=True)
    return df


def ext_temp_corners(dev_data_path: str, device: str, corners: str) -> pd.DataFrame:
    """Extract temperature corners from excel file.
    Args:
        dev_data_path (str): Path to excel file.
        device (str): Device name.
        corners (str): Corner names.
    Returns:
        pd.DataFrame: Dataframe with extracted data.
    """
    # Read Data
    df = pd.read_excel(dev_data_path)

    all_dfs = []
    for corner in corners:
        idf = df[
            ["Temperature (C)", "l (um)", "Unnamed: 2", f"res_{corner} Rev9 "]
        ].copy()
        idf.rename(
            columns={
                f"res_{corner} Rev9 ": "res_measured",
                "l (um)": "length",
                "Unnamed: 2": "info",
                "Temperature (C)": "temp",
            },
            inplace=True,
        )
        idf["corner"] = corner
        all_dfs.append(idf)

    df = pd.concat(all_dfs)
    df["width"] = df["info"].str.extract("w=([\d\.]+)").astype(float)
    df["device"] = device
    df["voltage"] = DEFAULT_VOLTAGE
    df.dropna(axis=0, inplace=True)
    df = df[["device", "corner", "length", "width", "voltage", "temp", "res_measured"]]
    df.drop_duplicates(inplace=True)
    return df


def run_sim(
    dirpath: str,
    device: str,
    length: float,
    width: float,
    corner: str,
    voltage: float,
    temp=25,
) -> dict:
    """Run simulation for a given device, length, width, corner, voltage and temperature.
    Args:
        dirpath (str): Path to directory where netlist is to be created.
        device (str): Device name.
        length (float): Device length.
        width (float): Device width.
        corner (str): Corner name.
        voltage (float): Voltage.
        temp (float, optional): Temperature. Defaults to 25.
    Returns:
        dict: Dictionary with simulation results.
    """
    netlist_tmp = "./device_netlists/res_op_analysis.spice"

    if "rm" in device or "tm" in device:
        terminals = "0"
    else:
        terminals = "0 0"

    info = {}
    info["device"] = device
    info["corner"] = corner
    info["temp"] = temp
    info["width"] = width
    info["length"] = length
    info["voltage"] = voltage

    width_str = "{:.3f}".format(width)
    length_str = "{:.3f}".format(length)
    temp_str = "{:.1f}".format(temp)
    voltage_str = "{:.2f}".format(voltage)

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
                    terminals=terminals,
                    temp=temp_str,
                    voltage=voltage_str,
                )
            )

    # Running xyce for each netlist
    try:
        call_simulator(netlist_path)
        # Find res in log
        try:
            res = find_res(f"{netlist_path}.log")
        except Exception:
            res = 0.0
    except Exception:
        res = 0.0

    info["res_sim_unscaled"] = res

    return info


def run_sims(
    df: pd.DataFrame, dirpath: str, num_workers=mp.cpu_count()
) -> pd.DataFrame:
    """Run simulations for all rows in dataframe.
    Args:
        df (pd.DataFrame): Dataframe with device, length, width, corner, voltage and temperature.
        dirpath (str): Path to directory where netlist is to be created.
        num_workers (int, optional): Number of workers. Defaults to mp.cpu_count().
    Returns:
        pd.DataFrame: Dataframe with simulation results.
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
                    row["voltage"],
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
    df = df[
        ["device", "corner", "length", "width", "voltage", "temp", "res_sim_unscaled"]
    ]
    df["res_sim"] = df["res_sim_unscaled"] * df["width"] / df["length"]
    return df


def main(num_cores: int):

    """Main function applies all regression steps"""
    # ======= Checking Xyce  =======
    Xyce_v_ = os.popen("Xyce  -v 2> /dev/null").read()
    if Xyce_v_ == "":
        logging.error("Xyce is not found. Please make sure Xyce is installed.")
        exit(1)
    elif "7.6" not in Xyce_v_:
        logging.error("Xyce version 7.6 is required.")
        exit(1)
    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    main_regr_dir = "res_regr"

    # res W&L var.
    corners = ["typical", "ff", "ss"]

    devices = [
        "nplus_u",
        "pplus_u",
        "nplus_s",
        "pplus_s",
        "npolyf_u",
        "ppolyf_u",
        "npolyf_s",
        "ppolyf_s",
        "ppolyf_u_1k",
        "ppolyf_u_2k",
        "ppolyf_u_1k_6p0",
        "ppolyf_u_2k_6p0",
        "ppolyf_u_3k",
        "rm1",
        "rm2",
        "rm3",
        "tm6k",
        "tm9k",
        "tm11k",
        "tm30k",
        "nwell",
    ]

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(f"{dev_path}", exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {dev}")

        wl_data_files = glob.glob(
            f"../../180MCU_SPICE_DATA/Resistor/RES*-wl-{dev}.nl*.xlsx"
        )
        if len(wl_data_files) < 1:
            logging.info(f"# Can't find wl file for device: {dev}")
            wl_file = ""
        else:
            wl_file = os.path.abspath(wl_data_files[0])
        logging.info(f"# W/L data points file : {wl_file}")

        temp_data_files = glob.glob(
            f"../../180MCU_SPICE_DATA/Resistor/RES*-temp-{dev}.nl*.xlsx"
        )
        if len(temp_data_files) < 1:
            logging.error(f"# Can't find temperature file for device: {dev}")
            temp_file = ""
        else:
            temp_file = os.path.abspath(temp_data_files[0])
        logging.info(f"# Temperature data points file : {temp_file}")

        if wl_file == "" and temp_file == "":
            logging.info(f"# No datapoints available for validation for device {dev}")
            continue

        if wl_file != "":
            meas_df_room_temp = ext_const_temp_corners(wl_file, dev, corners)
        else:
            meas_df_room_temp = []

        if temp_file != "":
            temperature_corners_df = ext_temp_corners(temp_file, dev, corners)
        else:
            temperature_corners_df = []

        if len(meas_df_room_temp) > 0 and len(temperature_corners_df) > 0:
            meas_df = pd.concat([meas_df_room_temp, temperature_corners_df])
        elif len(meas_df_room_temp) > 0 and len(temperature_corners_df) < 1:
            meas_df = meas_df_room_temp
        elif len(meas_df_room_temp) < 1 and len(temperature_corners_df) > 0:
            meas_df = temperature_corners_df

        logging.info(f"# Device {dev} number of measured_datapoints : {len(meas_df)}")

        sim_df = run_sims(meas_df, dev_path, num_cores)
        logging.info(f"# Device {dev} number of simulated datapoints : {len(sim_df)}")

        merged_df = meas_df.merge(
            sim_df, on=["device", "corner", "length", "width", "temp"], how="left"
        )
        merged_df["error"] = (
            np.abs(merged_df["res_sim"] - merged_df["res_measured"])
            * 100.0
            / merged_df["res_measured"]
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
    main(workers_count)
