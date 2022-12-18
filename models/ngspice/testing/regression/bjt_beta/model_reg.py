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

def find_bjt_beta(filename):
    """
    Find res in log
    """
    cmd = 'grep "bjt_bat = " {} | head -n 1'.format(filename)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return float(process.communicate()[0][:-1].decode("utf-8").split(" ")[2])

def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    return os.system(f"ngspice -b -a {file_name} -o {file_name}.log > {file_name}.log")

def ext_beta_corners(dev_data_path, device,vb , vc ,Id_sim, step,list_devices):
    # Read Data
    df = pd.read_excel(dev_data_path)
    corners = df["corners"].count()

    all_dfs = []
    for i in range(corners):

        k = i
        if i >= len(list_devices):
            while k >= len(list_devices):
                k = k - len(list_devices)

        # Special case for 1st measured values
        if i == 0:
            if device == "pnp":
                temp_vb = vb
                vb = "-vb "
            # measured Id_sim 0
            idf = df[[f"{vb}", f"{vc}{step[0]}", f"{vc}{step[1]}", f"{vc}{step[2]}"]].copy()
            idf.rename(
                columns={
                    f"{vb}": "base_volt",
                    f"{vc}{step[0]}": "coll_volt_s1",
                    f"{vc}{step[1]}": "coll_volt_s2",
                    f"{vc}{step[2]}": "coll_volt_s3"
                },
                inplace=True,
            )
            idf.to_csv(
                f"{device}/measured_{Id_sim[0]}/{i}_measured_{list_devices[k]}.csv",
                index=False,
            )
            
            idf["corner"] = corners
            all_dfs.append(idf)

            print(all_dfs)

            if device == "pnp":
                vb = temp_vb

            # measured Id_sim 1
            idf = df[[f"{vb}", f"{vc}{step[0]}", f"{vc}{step[1]}", f"{vc}{step[2]}"]].copy()
            idf.rename(
                columns={
                    f"{vb}": "base_volt",
                    f"{vc}{step[0]}.{2*i+1}": "coll_volt_s1",
                    f"{vc}{step[1]}.{2*i+1}": "coll_volt_s2",
                    f"{vc}{step[2]}.{2*i+1}": "coll_volt_s3"
                },
                inplace=True,
            )
        else:
            # measured Id_sim 0
            idf = df[[f"{vb}", f"{vc}{step[0]}", f"{vc}{step[1]}", f"{vc}{step[2]}"]].copy()
            idf.rename(
                columns={
                    f"{vb}": "base_volt",
                    f"{vc}{step[0]}.{2*i}": "coll_volt_s1",
                    f"{vc}{step[1]}.{2*i}": "coll_volt_s2",
                    f"{vc}{step[2]}.{2*i}": "coll_volt_s3"
                },
                inplace=True,
            )
            
            idf["corner"] = corners
            all_dfs.append(idf)

            # measured Id_sim 1
            idf = df[[f"{vb}", f"{vc}{step[0]}", f"{vc}{step[1]}", f"{vc}{step[2]}"]].copy()
            idf.rename(
                columns={
                    f"{vb}": "base_volt",
                    f"{vc}{step[0]}.{2*i+1}": "coll_volt_s1",
                    f"{vc}{step[1]}.{2*i+1}": "coll_volt_s2",
                    f"{vc}{step[2]}.{2*i+1}": "coll_volt_s3"
                },
                inplace=True,
            )

        

    df = pd.concat(all_dfs)
    df["device"] = device
    df.dropna(axis=0, inplace=True)
    df = df[["device", "corner", "base_volt","coll_volt_s1","coll_volt_s2","coll_volt_s3"]]
    return df


def run_sim(dirpath, device, vc, ib, temp=25):
    """ Run simulation at specific information and corner """
    netlist_tmp = "./device_netlists/res_op_analysis.spice"


    info = {}
    info["device"] = device
    info["collector_voltage"] = vc
    info["base_current"] = ib
    info["temp"] = temp
    

    collector_volt_str = "{:.3f}".format(vc)
    base_curr_str = "{:.3f}".format(ib)
    temp_str = "{:.1f}".format(temp)

    netlist_path = f"{dirpath}/{device}_netlists/netlist_w{collector_volt_str}_l{base_curr_str}_t{temp_str}.spice"

    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        os.makedirs(f"{dirpath}/{device}_netlists", exist_ok=True)

        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device,
                    i = ib,
                    temp=temp_str,
                    
                )
            )

    # Running ngspice for each netlist
    try:
        call_simulator(netlist_path)
        # Find res in log
        try:
            bjt_beta = find_bjt_beta(f"{netlist_path}.log")
        except Exception as e:
            bjt_beta = 0.0
    except Exception as e:
        bjt_beta = 0.0

    info["bjt_beta_sim_unscaled"] = bjt_beta

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
                    row["voltage"],
                    row["collector_current"],
                    row["base_voltage"]
                    
                )
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                print("Test case generated an exception: %s" % (exc))

    df = pd.DataFrame(results)
    print(df.columns)
    df = df[
        ["device","base_voltage" ,"collector_current", "temp"]
    ]
    
    return df


def main():

    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    main_regr_dir = "bjt_beta_regr"

    # bjt_beta var 
    vb = ["vbp (V)", "-vb "]
    vc = ["vcp =", "vc =-"]
    Id_sim = ["|Ic (A)|", "|Ib (A)|"]
    sweep = 101
    step = [1, 2, 3]


    devices = ["npn", "pnp"]
    list_devices = [
        [
            "npn_10p00x10p00",
            "npn_05p00x05p00",
            "npn_00p54x16p00",
            "npn_00p54x08p00",
            "npn_00p54x04p00",
            "npn_00p54x02p00",
        ],
        ["pnp_10p00x00p42", "pnp_05p00x00p42", "pnp_10p00x10p00", "pnp_05p00x05p00"],
    ]

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(f"{dev_path}", exist_ok=False)

        print("######" * 10)
        print(f"# Checking Device {dev}")

        beta_data_files = glob.glob(
            f"../../180MCU_SPICE_DATA/BJT/bjt_{dev}_beta_f.nl_out.xlsx"
        )
        if len(beta_data_files) < 1:
            print("# Can't find beta file for device: {}".format(dev))
            beta_file = ""
        else:
            beta_file = beta_data_files[0]
        print("# beta data points file : ", beta_file)


        if beta_file == "" :
            print(f"# No datapoints available for validation for device {dev}")
            continue

        if beta_file != "":
            meas_df = ext_beta_corners(beta_file, dev ,vb[i] , vc[i] ,Id_sim, step,list_devices)
        else:
            meas_df = []


        

        print("# Device {} number of measured_datapoints : ".format(dev), len(meas_df))

        sim_df = run_sims(meas_df, dev_path, 3)
        #print("# Device {} number of simulated datapoints : ".format(dev), len(sim_df))

        #merged_df = meas_df.merge(
        #    sim_df, on=["device", "corner", "length", "width", "temp"], how="left"
        #)
        #merged_df["error"] = (
        #    np.abs(merged_df["res_sim"] - merged_df["res_measured"])
        #    * 100.0
        #    / merged_df["res_measured"]
        #)

        #merged_df.to_csv(f"{dev_path}/error_analysis.csv", index=False)

        #print(
        #    "# Device {} min error: {:.2f} , max error: {:.2f}, mean error {:.2f}".format(
        #        dev,
        #        merged_df["error"].min(),
        #        merged_df["error"].max(),
        #        merged_df["error"].mean(),
        #    )
        #)

        #if merged_df["error"].max() < PASS_THRESH:
        #    print("# Device {} has passed regression.".format(dev))
        #else:
        #    print("# Device {} has failed regression. Needs more analysis.".format(dev))

        #print("\n\n")

        
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
