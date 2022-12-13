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
  model_reg.py [--num_cores=<num>]

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

import subprocess
import glob

import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

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


def ext_measured(dev_data_path, device, corners):
    # Read Data
    df = pd.read_excel(dev_data_path)

    length = []
    width = []
    corner = []
    moscap_meas = []

    for i in range(len(df)):

        a_str = df["Unnamed: 2"][i]  # area_string parameter
        moscap_corners = df["corners"][i]
        moscap_val = df[f"CV (fF)"][i]

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
    df = df[["device", "corner", "length", "width", "temp", "moscap_measured"]]

    return df


def run_sim(dirpath, device, length, width, corner, temp=25):
    """ Run simulation at specific information and corner """
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

        except Exception as e:
            moscap = 0.0

    except Exception as e:
        moscap = 0.0

    # print(moscap)

    info["moscap_sim_unscaled"] = moscap

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
                print("Test case generated an exception: %s" % (exc))

    df = pd.DataFrame(results)
    df = df[["device", "corner", "length", "width", "temp", "moscap_sim_unscaled"]]

    df["moscap_sim"] = df["moscap_sim_unscaled"]
    return df


def main():

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

        print("######" * 10)
        print(f"# Checking Device {dev}")

        if "3v3" in dev:
            dev_ind = "3p3"
        else:
            dev_ind = "6p0"

        moscap3p3_data_files = glob.glob(
            f"../../180MCU_SPICE_DATA/Cap/moscap_cv_{dev_ind}.nl_out.xlsx"
        )
        if len(moscap3p3_data_files) < 1:
            print("# Can't find moscap_3p3 file for device: {}".format(dev))
            moscap3p3_file = ""
        else:
            moscap3p3_file = moscap3p3_data_files[0]
        print("# moscap_3p3 data points file : ", moscap3p3_file)

        if moscap3p3_file == "":
            print(f"# No datapoints available for validation for device {dev}")
            continue

        if moscap3p3_file != "":
            meas_df = ext_measured(moscap3p3_file, dev, corners)
        else:
            meas_df = []

        print("# Device {} number of measured_datapoints : ".format(dev), len(meas_df))

        sim_df = run_sims(meas_df, dev_path, 3)
        print("# Device {} number of simulated datapoints : ".format(dev), len(sim_df))

        merged_df = meas_df.merge(
            sim_df, on=["device", "corner", "length", "width", "temp"], how="left"
        )

        merged_df["error"] = (
            np.abs(merged_df["moscap_sim"] - merged_df["moscap_measured"])
            * 100.0
            / merged_df["moscap_measured"]
        )

        merged_df.to_csv(f"{dev_path}/error_analysis.csv", index=False)

        print(
            "# Device {} min error: {:.2f} , max error: {:.2f}, mean error {:.2f}".format(
                dev,
                merged_df["error"].min(),
                merged_df["error"].max(),
                merged_df["error"].mean(),
            )
        )

        if merged_df["error"].max() < PASS_THRESH:
            print("# Device {} has passed regression.".format(dev))
        else:
            print("# Device {} has failed regression. Needs more analysis.".format(dev))

        print("\n\n")


# # ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================

if __name__ == "__main__":

    # Args
    arguments = docopt(__doc__, version="comparator: 0.1")
    workers_count = (
        os.cpu_count() * 2
        if arguments["--num_cores"] == None
        else int(arguments["--num_cores"])
    )

    # Calling main function
    main()
