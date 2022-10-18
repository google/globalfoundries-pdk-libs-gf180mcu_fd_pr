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

import subprocess
import glob

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

PASS_THRESH = 2.0
DEFAULT_TEMP = 25.0
DEFAULT_VOLTAGE = 1.0


def find_res(filename):
    """
    Find res in log
    """
    cmd = 'grep "res = " {} | head -n 1'.format(filename)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return float(process.communicate()[0][:-1].decode("utf-8").split(" ")[2])

def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    return os.system(f"ngspice -b -a {file_name} -o {file_name}.log > {file_name}.log")

def ext_const_temp_corners(dev_data_path, device, corners):
    # Read Data
    df = pd.read_excel(dev_data_path)

    all_dfs = []
    for corner in corners:
        idf = df[["l (um)", "w (um)", f"res_{corner} Rev9 "]].copy()
        idf.rename(columns={f"res_{corner} Rev9 ": "res_measured", "l (um)": "length", "w (um)": "width"}, inplace=True)
        idf["corner"] = corner
        all_dfs.append(idf)
    
    df = pd.concat(all_dfs)
    df["temp"] = DEFAULT_TEMP
    df["device"] = device
    df["voltage"] = DEFAULT_VOLTAGE
    df.dropna(axis=0, inplace=True)
    df = df[["device", "corner", "length", "width", "voltage", "temp", "res_measured"]]
    return df

def ext_temp_corners(dev_data_path, device, corners):
    # Read Data
    df = pd.read_excel(dev_data_path)
    
    all_dfs = []
    for corner in corners:
        idf = df[["Temperature (C)", "l (um)", "Unnamed: 2", f"res_{corner} Rev9 "]].copy()
        idf.rename(columns={f"res_{corner} Rev9 ": "res_measured", "l (um)": "length", "Unnamed: 2": "info", "Temperature (C)": "temp"}, inplace=True)
        idf["corner"] = corner
        all_dfs.append(idf)
    
    df = pd.concat(all_dfs)
    df["width"] = df["info"].str.extract("w=([\d\.]+)").astype(float)
    df["device"] = device
    df["voltage"] = DEFAULT_VOLTAGE
    df.dropna(axis=0, inplace=True)
    df = df[["device", "corner", "length", "width", "voltage", "temp", "res_measured"]]
    return df

def run_sim(dirpath, device, length, width, corner, voltage, temp=25):
    """ Run simulation at specific information and corner """
    netlist_tmp = "./device_netlists/res_op_analysis.spice"      

    if "rm" in device or "tm" in device:
        terminals = "GND"
    else:
        terminals = "GND GND"      

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
            netlist.write(tmpl.render(device = device, 
                                      width = width_str, 
                                      length =  length_str, 
                                      corner = corner, 
                                      terminals = terminals, 
                                      temp = temp_str,
                                      voltage = voltage_str))

    # Running ngspice for each netlist
    try:
        call_simulator(netlist_path)
        # Find res in log
        try:
            res = find_res(f"{netlist_path}.log")
        except Exception as e:
            res = 0.0
    except Exception as e:
        res = 0.0
    
    info["res_sim_unscaled"] = res

    return info

def run_sims(df, dirpath, num_workers=mp.cpu_count()):
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures_list = []
        for j, row in df.iterrows():
            futures_list.append(executor.submit(run_sim, dirpath, row["device"], row["length"], row["width"], row["corner"], row["voltage"], row["temp"]))
        
        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                print('Test case generated an exception: %s' % (exc))
    
    df = pd.DataFrame(results)
    df = df[["device", "corner", "length", "width", "voltage", "temp", "res_sim_unscaled"]]
    df["res_sim"] = df["res_sim_unscaled"] * df["width"] / df["length"]
    return df


def main():
    main_regr_dir = "res_regr"

    # res W&L var. 
    corners  = ["typical","ff","ss"]        
    
    devices  = ["nplus_u" , "pplus_u" , "nplus_s" , "pplus_s" , "npolyf_u" , "ppolyf_u" , "npolyf_s" , "ppolyf_s" , "ppolyf_u_1k" , "ppolyf_u_2k" , "ppolyf_u_1k_6p0" ,
                "ppolyf_u_2k_6p0" , "ppolyf_u_3k" , "rm1" , "rm2" , "rm3" , "tm6k" , "tm9k" , "tm11k" , "tm30k" , "nwell"]
    
    
    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)
        
        os.makedirs(f"{dev_path}",exist_ok=False)

        print("######" * 10)
        print(f"# Checking Device {dev}")

        wl_data_files = glob.glob(f"../../180MCU_SPICE_DATA/Resistor/RES*-wl-{dev}.nl*.xlsx")
        if len(wl_data_files) < 1:
            print("# Can't find wl file for device: {}".format(dev))
            wl_file = ""
        else:
            wl_file = wl_data_files[0]
        print("# W/L data points file : ", wl_file)

        temp_data_files = glob.glob(f"../../180MCU_SPICE_DATA/Resistor/RES*-temp-{dev}.nl*.xlsx")
        if len(temp_data_files) < 1:
            print("# Can't find temperature file for device: {}".format(dev))
            temp_file = ""
        else:
            temp_file = temp_data_files[0]
        print("# Temperature data points file : ", temp_file)

        if wl_file == "" and temp_file == "":
            print(f"# No datapoints available for validation for device {dev}")
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
        
        print("# Device {} number of measured_datapoints : ".format(dev), len(meas_df))

        sim_df_room_temp = run_sims(meas_df_room_temp, dev_path, 3)
        print("# Device {} number of simulated datapoints : ".format(dev), len(sim_df_room_temp))
        
        merged_df = meas_df_room_temp.merge(sim_df_room_temp, on=["device", "corner", "length", "width", "temp"], how="left")
        merged_df["error"] = np.abs(merged_df["res_sim"] - merged_df["res_measured"]) * 100.0 / merged_df["res_measured"]
        
        merged_df.to_csv(f"{dev_path}/error_analysis.csv", index=False)

        print("# Device {} min error: {:.2f} , max error: {:.2f}, mean error {:.2f}".format(dev,
                                                                                            merged_df["error"].min(), 
                                                                                            merged_df["error"].max(),
                                                                                            merged_df["error"].mean()))

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
    arguments     = docopt(__doc__, version='comparator: 0.1')
    workers_count = os.cpu_count()*2 if arguments["--num_cores"] == None else int(arguments["--num_cores"])
    
    # Calling main function 
    main()
