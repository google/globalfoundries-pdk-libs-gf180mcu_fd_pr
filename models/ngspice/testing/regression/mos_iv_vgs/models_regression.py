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

def ext_measured(dev_data_path, device):
    # Read Data
    read_file = pd.read_excel(dev_data_path)
    read_file.to_csv(f"mos_iv_regr/{device}/{device}.csv", index=False, header=True)
    df = pd.read_csv(f"mos_iv_regr/{device}/{device}.csv")

    all_dfs = []
    loops = 53
    
    # for pmos
    if device in ["pfet_03v3_iv", "pfet_06v0_iv"]:
        idf = df[["-Id (A)", "-vgs ", "vbs =0" , "vbs =0.825" , "vbs =1.65" ,"vbs =2.48" ,"vbs =3.3"]].copy()
        idf.rename(columns={"-vgs ": "measured_vgs0",
                            "vbs =0": "measured_vbs0 =0",
                            "vbs =0.825": "measured_vbs0 =0.825",
                            "vbs =1.65": "measured_vbs0 =1.65",
                            "vbs =2.48": "measured_vbs0 =2.48",
                            "vbs =3.3": "measured_vbs0 =3.3",
        },inplace=True)
    else:
        # for nmos
        idf = df[["Id (A)", "vgs ", "vbs =0" , "vbs =-0.825" , "vbs =-1.65" ,"vbs =-2.48" ,"vbs =-3.3"]].copy()
        idf.rename(columns={"vgs ": "measured_vgs0",
                            "vbs =0": "measured_vbs0 =0",
                            "vbs =-0.825": "measured_vbs0 =-0.825",
                            "vbs =-1.65": "measured_vbs0 =-1.65",
                            "vbs =-2.48": "measured_vbs0 =-2.48",
                            "vbs =-3.3": "measured_vbs0 =-3.3",
        },inplace=True)


    idf.dropna(inplace=True)
    all_dfs.append(idf)
    for i in range(loops):
        if device in ["pfet_03v3_iv", "pfet_06v0_iv"]:
            if i ==0:
                idf = df[[f"-vgs (V)", f"vbs =0.{i+1}" , f"vbs =0.825.{i+1}" , f"vbs =1.65.{i+1}" ,f"vbs =2.48.{i+1}" ,f"vbs =3.3.{i+1}"]].copy()

                idf.rename(
                    columns={
                        "-vgs (V)": "measured_vgs1",
                        f"vbs =0.{i+1}": f"measured_vbs{i+1} =0",
                        f"vbs =0.825.{i+1}": f"measured_vbs{i+1} =0.825",
                        f"vbs =1.65.{i+1}": f"measured_vbs{i+1} =1.65",
                        f"vbs =2.48.{i+1}": f"measured_vbs{i+1} =2.48",
                        f"vbs =3.3.{i+1}": f"measured_vbs{i+1} =3.3",

                    },
                    inplace=True,
                )
            else:
                idf = df[[f"-vgs (V).{i}", f"vbs =0.{i+1}" , f"vbs =0.825.{i+1}" , f"vbs =1.65.{i+1}" ,f"vbs =2.48.{i+1}" ,f"vbs =3.3.{i+1}"]].copy()

                idf.rename(            
                    columns={
                        f"-vgs (V).{i}": f"measured_vgs{i+1}",
                        f"vbs =0.{i+1}": f"measured_vbs{i+1} =0",
                        f"vbs =0.825.{i+1}": f"measured_vbs{i+1} =0.825",
                        f"vbs =1.65.{i+1}": f"measured_vbs{i+1} =1.65",
                        f"vbs =2.48.{i+1}": f"measured_vbs{i+1} =2.48",
                        f"vbs =3.3.{i+1}": f"measured_vbs{i+1} =3.3",

                    },
                    inplace=True,)
        else:
            if i ==0:
                idf = df[[f"vgs (V)", f"vbs =0.{i+1}" , f"vbs =-0.825.{i+1}" , f"vbs =-1.65.{i+1}" ,f"vbs =-2.48.{i+1}" ,f"vbs =-3.3.{i+1}"]].copy()

                idf.rename(
                    columns={
                        "vgs (V)": "measured_vgs1",
                        f"vbs =0.{i+1}": f"measured_vbs{i+1} =0",
                        f"vbs =-0.825.{i+1}": f"measured_vbs{i+1} =-0.825",
                        f"vbs =-1.65.{i+1}": f"measured_vbs{i+1} =-1.65",
                        f"vbs =-2.48.{i+1}": f"measured_vbs{i+1} =-2.48",
                        f"vbs =-3.3.{i+1}": f"measured_vbs{i+1} =-3.3",

                    },
                    inplace=True,
                )
            else:
                idf = df[[f"vgs (V).{i}", f"vbs =0.{i+1}" , f"vbs =-0.825.{i+1}" , f"vbs =-1.65.{i+1}" ,f"vbs =-2.48.{i+1}" ,f"vbs =-3.3.{i+1}"]].copy()

                idf.rename(            
                    columns={
                        f"vgs (V).{i}": f"measured_vgs{i+1}",
                        f"vbs =0.{i+1}": f"measured_vbs{i+1} =0",
                        f"vbs =-0.825.{i+1}": f"measured_vbs{i+1} =-0.825",
                        f"vbs =-1.65.{i+1}": f"measured_vbs{i+1} =-1.65",
                        f"vbs =-2.48.{i+1}": f"measured_vbs{i+1} =-2.48",
                        f"vbs =-3.3.{i+1}": f"measured_vbs{i+1} =-3.3",

                    },
                    inplace=True,
                )
        
        idf.dropna(inplace=True) 
        all_dfs.append(idf)

    dfs = pd.concat(all_dfs, axis=1)
    dfs.dropna(inplace=True)
    return dfs


def main():

    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    main_regr_dir = "mos_iv_regr"


    devices = [
            "nfet_03v3_iv",
            "pfet_03v3_iv",
            "nfet_06v0_iv",
            "pfet_06v0_iv",
            "nfet_06v0_nvt_iv",
        ]

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(f"{dev_path}", exist_ok=False)

        print("######" * 10)
        print(f"# Checking Device {dev}")

        data_files = glob.glob(
            f"../../180MCU_SPICE_DATA/MOS/{dev}.nl_out.xlsx"
        )
        if len(data_files) < 1:
            print("# Can't find file for device: {}".format(dev))
            file = ""
        else:
            file = data_files[0]
        print("#  data points file : ", file)


        if file != "":
            meas_df_room_temp = ext_measured(file, dev)
        else:
            meas_df_room_temp = []


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
