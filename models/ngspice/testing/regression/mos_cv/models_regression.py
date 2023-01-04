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
import glob

pd.options.mode.chained_assignment = None  # default='warn'
# constants
PASS_THRESH = 2.0

MOS = [0, -0.825, -1.65, -2.475, -3.3]
PMOS3P3_VPS = ["-0", 0.825, 1.65, 2.475, 3.3]
NMOS6P0_VPS = [0,-1, -2, -3]
PMOS6P0_VPS = ["-0",1, 2, 3]

MOS1 = [0, 1.1, 2.2, 3.3]
PMOS3P3_VPS1 = ["-0" , -1.1, -2.2 , -3.3]
NMOS6P0_VPS1 = [0, 2, 4, 6]
PMOS6P0_VPS1 = ["-0", -2, -4, -6]
# #######################


def ext_measured(dev_data_path, device):
    """Extracting the measured data of  devices from excel sheet

    Args:
         dev_data_path(str): path to the data sheet
         devices(str):  undertest device

    Returns:
         dfs(pd.DataFrame): A data frame contains all extracted data

    """

    # Read Data
    read_file = pd.read_excel(dev_data_path)
    read_file.to_csv(
        f"mos_cv_regr/{device}/{device}.csv", index=False, header=True
    )

    df = pd.read_csv(f"mos_cv_regr/{device}/{device}.csv")
    loops = int( 0.5 * df["L (um)"].count())
    all_dfs1 = []
    all_dfs2 = []
    all_dfs3 = []

    if device == "pfet_03v3":
        mos = PMOS3P3_VPS
        mos1 = PMOS3P3_VPS1
    elif device == "pfet_06v0":
        mos = PMOS6P0_VPS
        mos1 = PMOS6P0_VPS1
    elif device == "nfet_06v0":
        mos = NMOS6P0_VPS
        mos1 = NMOS6P0_VPS1
    elif device == "nfet_06v0_nvt":
        mos = NMOS6P0_VPS
        mos1 = NMOS6P0_VPS1
    else:
        mos = MOS
        mos1 = MOS1

    vgs="Vgs (V)"
    vds="Vds (V)"
    if device in ["pfet_03v3","pfet_06v0"]:
            vgs="-Vgs (V)"
            vds="-Vds (V)"
    for i in range(loops):
        width = df["W (um)"].iloc[ i]
        length = df["L (um)"].iloc[i]
  


        if i == 0:


            if device in ["nfet_03v3","pfet_03v3"]:
                idf1 = df[
                    [
                        vgs ,
                        f"Vbs={mos[0]}",
                        f"Vbs={mos[1]}",
                        f"Vbs={mos[2]}",
                        f"Vbs={mos[3]}",
                        f"Vbs={mos[4]}"
                    ]
                ].copy()

                idf1.rename(
                    columns={
                        vgs: "vgs",
                        f"Vbs={mos[0]}": f"measured_vbs{i}={mos[0]}",
                        f"Vbs={mos[1]}": f"measured_vbs{i}={mos[1]}",
                        f"Vbs={mos[2]}": f"measured_vbs{i}={mos[2]}",
                        f"Vbs={mos[3]}": f"measured_vbs{i}={mos[3]}",
                        f"Vbs={mos[4]}": f"measured_vbs{i}={mos[4]}"
                    },
                    inplace=True,
                )
            else:
                idf1 = df[
                    [
                        vgs ,
                        f"Vbs={mos[0]}",
                        f"Vbs={mos[1]}",
                        f"Vbs={mos[2]}",
                        f"Vbs={mos[3]}"
                    ]
                ].copy()

                idf1.rename(
                    columns={
                        vgs: "vgs",
                        f"Vbs={mos[0]}": f"measured_vbs{i}={mos[0]}",
                        f"Vbs={mos[1]}": f"measured_vbs{i}={mos[1]}",
                        f"Vbs={mos[2]}": f"measured_vbs{i}={mos[2]}",
                        f"Vbs={mos[3]}": f"measured_vbs{i}={mos[3]}"
                    },
                    inplace=True,
                )    
            idf2 = df[
                [
                    vds,
                    f"Vgs={mos1[0]}",
                    f"Vgs={mos1[1]}",
                    f"Vgs={mos1[2]}",
                    f"Vgs={mos1[3]}"
                ]
            ].copy()

            idf2.rename(
                columns={
                    vds: "vds",
                    f"Vgs={mos1[0]}": f"measured_vgs{i}={mos1[0]}",
                    f"Vgs={mos1[1]}": f"measured_vgs{i}={mos1[1]}",
                    f"Vgs={mos1[2]}": f"measured_vgs{i}={mos1[2]}",
                    f"Vgs={mos1[3]}": f"measured_vgs{i}={mos1[3]}"
                },
                inplace=True,
            )
            idf3 = df[
                [
                    vds,
                    f"Vgs={mos1[0]}.{i+1}",
                    f"Vgs={mos1[1]}.{i+1}",
                    f"Vgs={mos1[2]}.{i+1}",
                    f"Vgs={mos1[3]}.{i+1}"
                ]
            ].copy()

            idf3.rename(
                columns={
                    vds: "vds",
                    f"Vgs={mos1[0]}.{i+1}": f"measured_vgs{i}={mos1[0]}",
                    f"Vgs={mos1[1]}.{i+1}": f"measured_vgs{i}={mos1[1]}",
                    f"Vgs={mos1[2]}.{i+1}": f"measured_vgs{i}={mos1[2]}",
                    f"Vgs={mos1[3]}.{i+1}": f"measured_vgs{i}={mos1[3]}"
                },
                inplace=True,
            )           
        else:
            
            if device in ["nfet_03v3","pfet_03v3"]:
                idf1 = df[
                    [
                        vgs,
                        f"Vbs={mos[0]}.{i}",
                        f"Vbs={mos[1]}.{i}",
                        f"Vbs={mos[2]}.{i}",
                        f"Vbs={mos[3]}.{i}",
                        f"Vbs={mos[4]}.{i}"
                    ]
                ].copy()

                idf1.rename(
                    columns={
                        vgs: "vgs",
                        f"Vbs={mos[0]}.{i}": f"measured_vbs{i}={mos[0]}",
                        f"Vbs={mos[1]}.{i}": f"measured_vbs{i}={mos[1]}",
                        f"Vbs={mos[2]}.{i}": f"measured_vbs{i}={mos[2]}",
                        f"Vbs={mos[3]}.{i}": f"measured_vbs{i}={mos[3]}",
                        f"Vbs={mos[4]}.{i}": f"measured_vbs{i}={mos[4]}"
                    },
                    inplace=True,
                )
            else:
                idf1 = df[
                    [
                        vgs,
                        f"Vbs={mos[0]}.{i}",
                        f"Vbs={mos[1]}.{i}",
                        f"Vbs={mos[2]}.{i}",
                        f"Vbs={mos[3]}.{i}"
                    ]
                ].copy()

                idf1.rename(
                    columns={
                        vgs: "vgs",
                        f"Vbs={mos[0]}.{i}": f"measured_vbs{i}={mos[0]}",
                        f"Vbs={mos[1]}.{i}": f"measured_vbs{i}={mos[1]}",
                        f"Vbs={mos[2]}.{i}": f"measured_vbs{i}={mos[2]}",
                        f"Vbs={mos[3]}.{i}": f"measured_vbs{i}={mos[3]}"
                    },
                    inplace=True,
                )                    
            idf2 = df[
                [
                    vds,
                    f"Vgs={mos1[0]}.{2*i}",
                    f"Vgs={mos1[1]}.{2*i}",
                    f"Vgs={mos1[2]}.{2*i}",
                    f"Vgs={mos1[3]}.{2*i}"
                ]
            ].copy()

            idf2.rename(
                columns={
                    vds: "vds",
                    f"Vgs={mos1[0]}.{2*i}": f"measured_vgs{i}={mos1[0]}",
                    f"Vgs={mos1[1]}.{2*i}": f"measured_vgs{i}={mos1[1]}",
                    f"Vgs={mos1[2]}.{2*i}": f"measured_vgs{i}={mos1[2]}",
                    f"Vgs={mos1[3]}.{2*i}": f"measured_vgs{i}={mos1[3]}"
                },
                inplace=True,
            )
            idf3 = df[
                [
                    vds,
                    f"Vgs={mos1[0]}.{2*i + 1}",
                    f"Vgs={mos1[1]}.{2*i + 1}",
                    f"Vgs={mos1[2]}.{2*i + 1}",
                    f"Vgs={mos1[3]}.{2*i + 1}"
                ]
            ].copy()

            idf3.rename(
                columns={
                    vds: "vds",
                    f"Vgs={mos1[0]}.{2*i + 1}": f"measured_vgs{i}={mos1[0]}",
                    f"Vgs={mos1[1]}.{2*i + 1}": f"measured_vgs{i}={mos1[1]}",
                    f"Vgs={mos1[2]}.{2*i + 1}": f"measured_vgs{i}={mos1[2]}",
                    f"Vgs={mos1[3]}.{2*i + 1}": f"measured_vgs{i}={mos1[3]}"
                },
                inplace=True,
            )

        idf1["W (um)"] = width
        idf1["L (um)"] = length
        idf2["W (um)"] = width
        idf2["L (um)"] = length
        idf3["W (um)"] = width
        idf3["L (um)"] = length        
        
        idf1.dropna(inplace=True)
        all_dfs1.append(idf1)
        idf2.dropna(inplace=True)
        idf3.dropna(inplace=True)
        all_dfs2.append(idf2)
        all_dfs3.append(idf3)
    dfs1 = pd.concat(all_dfs1, axis=1)
    dfs1.drop_duplicates(inplace=True)
    dfs2 = pd.concat(all_dfs2, axis=1)
    dfs2.drop_duplicates(inplace=True)
    dfs3 = pd.concat(all_dfs3, axis=1)
    dfs3.drop_duplicates(inplace=True)        
    return dfs1,dfs2,dfs3


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    return os.system(
        f"ngspice -b -a {file_name} -o {file_name}.log > {file_name}.log"
    )


def run_sim(dirpath, device, width, length, nf):
    """Run simulation at specific information and corner
    Args:
        dirpath(str): path to the file where we write data
        device(str): the device instance will be simulated
        id_rds(str): select id or rds
        temp(float): a specific temp for simulation
        width(float): a specific width for simulation
        length(float): a specific length for simulation

    Returns:
        info(dict): results are stored in,
        and passed to the run_sims function to extract data
    """
    caps=["c","d","s"]
    for cap in caps:
        netlist_tmp = f"device_netlists_Cg{cap}/{device}.spice"

        info = {}
        info["device"] = device
        info["length"] = length
        info["width"] = width
        width_str = width
        length_str = length
        nf_str=nf

        s = f"netlist_w{width_str}_l{length_str}.spice"
        netlist_path = f"{dirpath}/{device}_netlists_Cg{cap}/{s}"
        s = f"simulated_W{width_str}_L{length_str}.csv"
        result_path = f"{dirpath}/simulated_Cg{cap}/{s}"
        os.makedirs(f"{dirpath}/simulated_Cg{cap}", exist_ok=True)
        with open(netlist_tmp) as f:
            tmpl = Template(f.read())
            os.makedirs(f"{dirpath}/{device}_netlists_Cg{cap}", exist_ok=True)
            with open(netlist_path, "w") as netlist:
                netlist.write(
                    tmpl.render(
                        width=width_str,
                        length=length_str,
                        nf=nf_str
            
                    )
                )

        # Running ngspice for each netlist
        try:
            call_simulator(netlist_path)

            if os.path.exists(result_path):
                mos_iv = result_path
            else:
                mos_iv = "None"

        except Exception:
            mos_iv = "None"

        info["mos_cg{cap}_simulated"] = mos_iv

    return info


def run_sims(df, dirpath, device, num_workers=mp.cpu_count()):
    """passing netlists to run_sim function
        and storing the results csv files into dataframes

    Args:
        df(pd.DataFrame): dataframe passed from the ext_measured function
        dirpath(str): the path to the file where we write data
        id_rds(str): select id or rds
        num_workers=mp.cpu_count() (int): num of cpu used
        device(str): name of the device
    Returns:
        df(pd.DataFrame): dataframe contains simulated results
    """

    results = []
    df["nf"] = 1
    df["nf"][0] = 20
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=num_workers
    ) as executor:
        futures_list = []
        for j, row in df.iterrows():
            futures_list.append(
                executor.submit(
                    run_sim,
                    dirpath,
                    device,
                    row["W (um)"],
                    row["L (um)"],
                    row["nf"]
                )
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                print("Test case generated an exception: %s" % (exc))

    caps=["c","d","s"]
    for cap in caps:            
        sf = glob.glob(f"{dirpath}/simulated_Cg{cap}/*.csv")

        # sweeping on all generated cvs files
        for i in range(len(sf)):
            sdf = pd.read_csv(
                sf[i],
                header=None,
                delimiter=r"\s+",
            )
            if cap=="c" and device in ["nfet_03v3","pfet_03v3"]:
                div_by=len(MOS)
            else:
                div_by=len(MOS1)

            sweep = int(sdf[0].count() / div_by)
            new_array = np.empty((sweep, 1 + int(sdf.shape[0] / sweep)))

            new_array[:, 0] = sdf.iloc[:sweep, 0]
            times = int(sdf.shape[0] / sweep)

            for j in range(times):
                new_array[:, (j + 1)] = sdf.iloc[j * sweep: (j + 1) * sweep, 1]

            # Writing final simulated data 1
            sdf = pd.DataFrame(new_array)
            if (cap=="c"):
                sdf.rename(
                    columns={
                        0: "vgs",
                        1: "vb1",
                        2: "vb2",
                        3: "vb3",
                        4: "vb4",
                        5: "vb5"
                    },
                    inplace=True,
                )

            else:
                sdf.rename(
                    columns={
                        0: "vds",
                        1: "vgs1",
                        2: "vgs2",
                        3: "vgs3",
                        4: "vgs4",
                    },
                    inplace=True,
                )
            sdf.to_csv(sf[i], index=False)

        df = pd.DataFrame(results)
    return df


def error_cal(
    df: pd.DataFrame,
    sim_df: pd.DataFrame,
    meas_df1: pd.DataFrame,
    meas_df2: pd.DataFrame,
    meas_df3: pd.DataFrame,
    dev_path: str,
    device: str,
) -> None:
    """error function calculates the error between measured, simulated data

    Args:
        df(pd.DataFrame): Dataframe contains devices and csv files
          which represent measured, simulated data
        sim_df(pd.DataFrame): Dataframe contains devices and csv files simulated
        meas_df(pd.DataFrame): Dataframe contains devices and csv files measured
        dev_path(str): The path in which we write data
        id_rds(str): select id or rds

    """

    # adding error columns to the merged dataframe
    merged_dfs = list()
    if device == "pfet_03v3":
        mos = PMOS3P3_VPS
        mos1 = PMOS3P3_VPS1
    elif device == "pfet_06v0":
        mos = PMOS6P0_VPS
        mos1 = PMOS6P0_VPS1
    elif device == "nfet_06v0":
        mos = NMOS6P0_VPS
        mos1 = NMOS6P0_VPS1
    elif device == "nfet_06v0_nvt":
        mos = NMOS6P0_VPS
        mos1 = NMOS6P0_VPS1
    else:
        mos = MOS
        mos1 = MOS1
    caps=["c","d","s"]
    
    for cap in caps:
        if cap=="c":
            meas_df=meas_df1
        elif cap=="d":
            meas_df=meas_df2
        else:
            meas_df=meas_df3

        for i in range(len(sim_df)):
            length = sim_df["length"].iloc[int(i)]
            w = sim_df["width"].iloc[int(i)]
            s = f"simulated_W{w}_L{length}.csv"
            sim_path = f"mos_cv_regr/{device}/simulated_Cg{cap}/{s}"

            simulated_data = pd.read_csv(sim_path)

            if cap =="c":
                if device in ["nfet_03v3","pfet_03v3"]:
                    measured_data = meas_df[
                        [
                            f"measured_vbs{i}={mos[0]}",
                            f"measured_vbs{i}={mos[1]}",
                            f"measured_vbs{i}={mos[2]}",
                            f"measured_vbs{i}={mos[3]}",
                            f"measured_vbs{i}={mos[4]}"
                        ]
                    ].copy()
                    measured_data.rename(
                        columns={
                            f"measured_vbs{i}={mos[0]}": "measured_v1",
                            f"measured_vbs{i}={mos[1]}": "measured_v2",
                            f"measured_vbs{i}={mos[2]}": "measured_v3",
                            f"measured_vbs{i}={mos[3]}": "measured_v4",
                            f"measured_vbs{i}={mos[4]}": "measured_v5"
                        },
                        inplace=True,
                    )
                else:

                    measured_data = meas_df[
                        [
                            f"measured_vbs{i}={mos[0]}",
                            f"measured_vbs{i}={mos[1]}",
                            f"measured_vbs{i}={mos[2]}",
                            f"measured_vbs{i}={mos[3]}"
                        ]
                    ].copy()
                    measured_data.rename(
                        columns={
                            f"measured_vbs{i}={mos[0]}": "measured_v1",
                            f"measured_vbs{i}={mos[1]}": "measured_v2",
                            f"measured_vbs{i}={mos[2]}": "measured_v3",
                            f"measured_vbs{i}={mos[3]}": "measured_v4"
                        },
                        inplace=True,
                    )
                measured_data["vgs"] = simulated_data["vgs"]
            else:
                measured_data = meas_df[
                    [
                        f"measured_vgs{i}={mos1[0]}",
                        f"measured_vgs{i}={mos1[1]}",
                        f"measured_vgs{i}={mos1[2]}",
                        f"measured_vgs{i}={mos1[3]}"
                    ]
                ].copy()
                measured_data.rename(
                    columns={
                        f"measured_vgs{i}={mos1[0]}": "measured_v1",
                        f"measured_vgs{i}={mos1[1]}": "measured_v2",
                        f"measured_vgs{i}={mos1[2]}": "measured_v3",
                        f"measured_vgs{i}={mos1[3]}": "measured_v4"
                    },
                    inplace=True,
                )
                measured_data["vds"] = simulated_data["vds"]


            result_data = simulated_data.merge(measured_data, how="left")

  
            if cap =="c":
                  
                result_data["step1_error"] = (
                    np.abs(result_data["measured_v1"] - result_data["vb1"])
                    * 100.0
                    / (result_data["measured_v1"])
                )
                result_data["step2_error"] = (
                    np.abs(result_data["measured_v2"] - result_data["vb2"])
                    * 100.0
                    / (result_data["measured_v2"])
                )
                result_data["step3_error"] = (
                    np.abs(result_data["measured_v3"] - result_data["vb3"])
                    * 100.0
                    / (result_data["measured_v3"])
                )
                result_data["step4_error"] = (
                    np.abs(result_data["measured_v4"] - result_data["vb4"])
                    * 100.0
                    / (result_data["measured_v4"])
                )
                if device in ["nfet_03v3","pfet_03v3"]:
                    result_data["step5_error"] = (
                        np.abs(result_data["measured_v5"] - result_data["vb5"])
                        * 100.0
                        / (result_data["measured_v5"])
                    )        

                    result_data["error"] = (
                        np.abs(
                            result_data["step1_error"]
                            + result_data["step2_error"]
                            + result_data["step3_error"]
                            + result_data["step4_error"]
                            + result_data["step5_error"]
                        )
                        / 5
                    )
                else:
                    result_data["error"] = (
                        np.abs(
                            result_data["step1_error"]
                            + result_data["step2_error"]
                            + result_data["step3_error"]
                            + result_data["step4_error"]
                        )
                        / 4
                    )

            else:
                result_data["step1_error"] = (
                    np.abs(result_data["measured_v1"] - result_data["vgs1"])
                    * 100.0
                    / (result_data["measured_v1"])
                )
                result_data["step2_error"] = (
                    np.abs(result_data["measured_v2"] - result_data["vgs2"])
                    * 100.0
                    / (result_data["measured_v2"])
                )
                result_data["step3_error"] = (
                    np.abs(result_data["measured_v3"] - result_data["vgs3"])
                    * 100.0
                    / (result_data["measured_v3"])
                )
                result_data["step4_error"] = (
                    np.abs(result_data["measured_v4"] - result_data["vgs4"])
                    * 100.0
                    / (result_data["measured_v4"])
                )
                result_data["error"] = (
                    np.abs(
                        result_data["step1_error"]
                        + result_data["step2_error"]
                        + result_data["step3_error"]
                        + result_data["step4_error"]
                    )
                    / 4
                )

            merged_dfs.append(result_data)
            merged_out = pd.concat(merged_dfs)
            merged_out.fillna(0, inplace=True)
            merged_out.to_csv(
                f"{dev_path}/error_analysis_Cg{cap}.csv", index=False
            )
    return None


def main():
    """Main function applies all regression steps"""
    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    main_regr_dir = "mos_cv_regr"

    devices = [
        "nfet_03v3",
        "pfet_03v3",
        "nfet_06v0",
        "pfet_06v0",
        "nfet_06v0_nvt"
    ]
    measured_data = ["3p3_cv","6p0_cv","6p0_nat_cv"]
    if os.path.exists(main_regr_dir) and os.path.isdir(main_regr_dir):
        shutil.rmtree(main_regr_dir)

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"


        os.makedirs(f"{dev_path}", exist_ok=False)

        print("######" * 10)
        print(f"# Checking Device {dev}")

        data_files = glob.glob(
            f"measured_data/{measured_data[int(i*0.5)]}.nl_out.xlsx"

        )
        if len(data_files) < 1:
            print("# Can't find file for device: {}".format(dev))
            file = ""
        else:
            file = data_files[0]
        print("#  data points file : ", file)

        if file != "":
            meas_df1,meas_df2,meas_df3 = ext_measured(file, dev)
        else:
            meas_df1 = []
            meas_df2 = []
            meas_df3 = []

        # meas_df1.to_csv("dd.csv")
        # meas_df2.to_csv("dd2.csv")
        # meas_df3.to_csv("dd3.csv")
        df1 = pd.read_csv(f"mos_cv_regr/{dev}/{dev}.csv")
        df2 = df1[["L (um)", "W (um)"]].copy()
        df2.dropna(inplace=True)
        loops = int( 0.5 * df2["L (um)"].count())
        df=df2[["L (um)", "W (um)"]].iloc[0:loops]
        sim_df_id = run_sims(df, dev_path, dev)

        print(
            "# Device {} number of measured_datapoints for cv : ".format(dev),
            len(sim_df_id) * (len(meas_df1)+len(meas_df2)+len(meas_df3)),
        )
        print(
            "# Device {} number of simulated datapoints for cv : ".format(dev),
            len(sim_df_id) * (len(meas_df1)+len(meas_df2)+len(meas_df3)),
        )
        print("\n\n")

        # passing dataframe to the error_calculation function
        # calling error function for creating statistical csv file

        error_cal(df, sim_df_id, meas_df1,meas_df2,meas_df3, dev_path, dev)

        caps=["c","d","s"]
    
        for cap in caps:
            # reading from the csv file contains all error data
            # merged_all contains all simulated, measured, error data
            merged_all = pd.read_csv(f"{dev_path}/error_analysis_Cg{cap}.csv")

            # calculating the error of each device and reporting it
            min_error_total = float()
            max_error_total = float()
            error_total = float()

            # number of rows in the final excel sheet
            num_rows = merged_all["error"].count()

            for n in range(num_rows):
                error_total += merged_all["error"][n]
                if merged_all["error"][n] > max_error_total:
                    max_error_total = merged_all["error"][n]
                elif merged_all["error"][n] < min_error_total:
                    min_error_total = merged_all["error"][n]

            mean_error_total = error_total / num_rows

            # Making sure that min, max, mean errors are not > 100%
            if min_error_total > 100:
                min_error_total = 100

            if max_error_total > 100:
                max_error_total = 100

            if mean_error_total > 100:
                mean_error_total = 100

            # printing min, max, mean errors to the consol
            print(
                "# Device {} min error: {:.2f}".format(dev, min_error_total),
                ", max error: {:.2f}, mean error {:.2f}".format(
                    max_error_total, mean_error_total
                ),
            )

            if max_error_total < PASS_THRESH:
                print("# Device {} has passed regression.".format(dev))
            else:
                print(
                    "# Device {} has failed regression.".format(
                        dev
                    )
                )
            print("\n\n")
    print("\n\n")


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

    # Calling main function
    main()