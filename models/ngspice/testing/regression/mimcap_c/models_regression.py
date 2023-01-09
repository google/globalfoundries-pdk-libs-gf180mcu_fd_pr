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
import logging

import subprocess
import glob

import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

DEFAULT_TEMP = 25.0
PASS_THRESH = 2.0

def find_mimcap(filename):
    """
    Find mimcap in log
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

    for i in range(len(df)):

        a_str = df["Unnamed: 2"][i]  # area_string parameter in the format "mim_1p5fF(100u x100u )"
        if type(a_str) == str :

            length.append(float(a_str.split("(")[1].split("x")[0].split("u")[0]))
            width.append(float(a_str.split("(")[1].split("x")[1].split("u")[0]))
        
        else :
            length.append(a_str)
            width.append(a_str)
    
    all_dfs = []
    for corner in corners:
        idf = df[[f"mimcap_{corner}"]].copy()
        idf.rename(
            columns={
                f"mimcap_{corner}": "mimcap_measured",
            },
            inplace=True,
        )
        idf["corner"] = corner
        idf["length"] = length
        idf["width"] = width
        all_dfs.append(idf)

    df = pd.concat(all_dfs)
    df["temp"] = DEFAULT_TEMP
    df["device"] = device
    df.dropna(axis=0, inplace=True)
    df = df[["device", "corner", "length", "width", "temp", "mimcap_measured"]]
    return df

def run_sim(dirpath, device, length, width, corner, temp=25):
    """ Run simulation at specific information and corner """
    netlist_tmp = "./device_netlists/mimcap.spice"


    info = {}
    info["device"] = device
    info["corner"] = corner
    info["temp"] = temp
    info["width"] = width
    info["length"] = length

    width_str = "{:.0f}".format(width)
    length_str = "{:.0f}".format(length)
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
        # Find mimcap in log
        try:
            mim = find_mimcap(f"{netlist_path}.log")
            
        except Exception as e:
            mim = 0.0
        
    except Exception as e:
        mim = 0.0
    
    info["mim_sim_unscaled"] = mim

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
    df = df[
        ["device", "corner", "length", "width", "temp","mim_sim_unscaled"]
    ]

    df["mim_sim"] = df["mim_sim_unscaled"]
    return df


def main():
        # ======= Checking ngspice  =======
    ngspice_v_ = os.popen("ngspice -v").read()
    if ngspice_v_ == "":
        logging.error("ngspice is not found. Please make sure ngspice is installed.")
        exit(1)
    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    main_regr_dir = "mimcap_regr"

    # mimcap var.
    corners = ["typical", "ff", "ss"]

    devices = [ 
        "cap_mim_1f5_m2m3_noshield",
        "cap_mim_1f0_m2m3_noshield",
        "cap_mim_2f0_m2m3_noshield",
        "cap_mim_1f5_m3m4_noshield",
        "cap_mim_1f0_m3m4_noshield",
        "cap_mim_2f0_m3m4_noshield",  
        "cap_mim_1f5_m4m5_noshield",
        "cap_mim_1f0_m4m5_noshield",
        "cap_mim_2f0_m4m5_noshield",
        "cap_mim_1f5_m5m6_noshield",
        "cap_mim_1f0_m5m6_noshield",
        "cap_mim_2f0_m5m6_noshield"          
    ]

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(f"{dev_path}", exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {dev}")

        mim_data_files = glob.glob(
            f"../../180MCU_SPICE_DATA/Cap/mimcap_fc.nl_out.xlsx"
        )
        if len(mim_data_files) < 1:
            logging.info(f"# Can't find mimcap file for device: {dev}")
            mim_file = ""
        else:
            mim_file = mim_data_files[0]
        logging.info(f"# mimcap data points file : {mim_file}" )

        if mim_file == "" :
            logging.info(f"# No datapoints available for validation for device {dev}")
            continue
            
        if mim_file != "":
            meas_df = ext_measured(mim_file, dev, corners)
        else:
            meas_df = []

        logging.info(f"# Device {dev} number of measured_datapoints : {len(meas_df)}")

        sim_df = run_sims(meas_df, dev_path, 3)
        logging.info(f"# Device {dev} number of simulated datapoints :{len(sim_df)}")

        merged_df = meas_df.merge(
            sim_df, on=["device", "corner", "length", "width", "temp"], how="left"
        )

        merged_df["error"] = (
            np.abs(merged_df["mim_sim"] - merged_df["mimcap_measured"])
            * 100.0
            / merged_df["mimcap_measured"]
        )

        merged_df.to_csv(f"{dev_path}/error_analysis.csv", index=False)
        m1=merged_df["error"].min()
        m2=merged_df["error"].max()
        m3=merged_df["error"].mean()
        logging.info(
            f"# Device {dev} min error: {m1:.2f} , max error: {m2:.2f}, mean error {m3:.2f}")

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
        if arguments["--num_cores"] == None
        else int(arguments["--num_cores"])
    )
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            logging.StreamHandler(),
        ],
        format=f"%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )
    
    # Calling main function
    main()

    
