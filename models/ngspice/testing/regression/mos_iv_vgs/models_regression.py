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
import logging

# CONSTANT VALUES
PASS_THRESH = 5.0

MOS_VGS = [0.8, 1.3, 1.8, 2.3, 2.8, 3.3]
PMOS3P3_VGS = [-0.8, -1.3, -1.8, -2.3, -2.8, -3.3]
NMOS6P0_VGS = [1, 2, 3, 4, 5, 6]
PMOS6P0_VGS = [-1, -2, -3, -4, -5, -6]
NMOS6P0_VGS_N = [0.25, 1.4, 2.55, 3.7, 4.85, 6]

VDS_N03V3 = "0 3.3 0.05"
VDS_P03V3 = "0 -3.3 -0.05"
VDS_N06V0 = "0 6.6 0.05"
VDS_P06V0 = "0 -6.6 -0.05"
VDS_N06V0_N = "0 6.6 0.05"

VGS_N03V3 = "0.8 3.3 0.5"
VGS_P03V3 = "-0.8 -3.3 -0.5"
VGS_N06V0 = "1 6 1"
VGS_P06V0 = "-1 -6 -1"
VGS_N06V0_N = "0.25 6 1.15"


def check_ngspice_version():
    """
    check_ngspice_version checks ngspice version and makes sure it would work with the models.
    """
    # ======= Checking ngspice  =======
    ngspice_v_ = os.popen("ngspice -v").read()

    if "ngspice-" not in ngspice_v_:
        logging.error("ngspice is not found. Please make sure ngspice is installed.")
        exit(1)
    else:
        version = int((ngspice_v_.split("\n")[1]).split(" ")[1].split("-")[1])
        logging.info(f"Your Klayout version is: ngspice {version}")
        if version <= 37:
            logging.error(
                "ngspice version is not supported. Please use ngspice version 38 or newer."
            )
            exit(1)


def ext_measured(dev_path, data_file, device) -> pd.DataFrame:
    """
    Extracting the measured data of  devices from excel sheet

    Args:
        dev_path (str): Path of device regression results
        data_file (str): Xlsx file contains measurement data
        device (str): Device under test

    Returns:
         dfs(pd.DataFrame): A data frame contains all extracted data
    """

    # Read Data
    read_file = pd.read_excel(data_file)

    data_file_path = os.path.join(dev_path, f"{device}.csv")
    read_file.to_csv(data_file_path, index=False, header=True)
    df = pd.read_csv(data_file_path)

    loops = df["L (um)"].count()
    all_dfs = []

    # Voltages setup
    if "pfet_03v3" in device:
        mos_vgs = PMOS3P3_VGS
    elif "pfet_06v0" in device:
        mos_vgs = PMOS6P0_VGS
    elif "nfet_06v0" in device and "nvt" not in device:
        mos_vgs = NMOS6P0_VGS
    elif "nfet_06v0_nvt" in device:
        mos_vgs = NMOS6P0_VGS_N
    else:
        mos_vgs = MOS_VGS

    width = df["W (um)"].iloc[0]
    length = df["L (um)"].iloc[0]

    ## PMOS
    if "pfet" in device:
        idf = df[
            [
                "-Id (A)",
                "-vds (V)",
                f"vgs ={mos_vgs[0]}",
                f"vgs ={mos_vgs[1]}",
                f"vgs ={mos_vgs[2]}",
                f"vgs ={mos_vgs[3]}",
                f"vgs ={mos_vgs[4]}",
                f"vgs ={mos_vgs[5]}",
            ]
        ].copy()
        idf.rename(
            columns={
                "-vds (V)": "vds",
                f"vgs ={mos_vgs[0]}": f"measured_vgs0 ={mos_vgs[0]}",
                f"vgs ={mos_vgs[1]}": f"measured_vgs0 ={mos_vgs[1]}",
                f"vgs ={mos_vgs[2]}": f"measured_vgs0 ={mos_vgs[2]}",
                f"vgs ={mos_vgs[3]}": f"measured_vgs0 ={mos_vgs[3]}",
                f"vgs ={mos_vgs[4]}": f"measured_vgs0 ={mos_vgs[4]}",
                f"vgs ={mos_vgs[5]}": f"measured_vgs0 ={mos_vgs[5]}",
            },
            inplace=True,
        )
    else:
        ## NMOS
        idf = df[
            [
                "Id (A)",
                "vds (V)",
                f"vgs ={mos_vgs[0]}",
                f"vgs ={mos_vgs[1]}",
                f"vgs ={mos_vgs[2]}",
                f"vgs ={mos_vgs[3]}",
                f"vgs ={mos_vgs[4]}",
                f"vgs ={mos_vgs[5]}",
            ]
        ].copy()
        idf.rename(
            columns={
                "vds (V)": "vds",
                f"vgs ={mos_vgs[0]}": f"measured_vgs0 ={mos_vgs[0]}",
                f"vgs ={mos_vgs[1]}": f"measured_vgs0 ={mos_vgs[1]}",
                f"vgs ={mos_vgs[2]}": f"measured_vgs0 ={mos_vgs[2]}",
                f"vgs ={mos_vgs[3]}": f"measured_vgs0 ={mos_vgs[3]}",
                f"vgs ={mos_vgs[4]}": f"measured_vgs0 ={mos_vgs[4]}",
                f"vgs ={mos_vgs[5]}": f"measured_vgs0 ={mos_vgs[5]}",
            },
            inplace=True,
        )

    idf.dropna(inplace=True)
    idf["W (um)"] = width
    idf["L (um)"] = length
    idf["temp"] = 25

    all_dfs.append(idf)

    # Temp setup
    temp_range = int(2 * loops / 3)

    for i in range(2 * loops - 1):
        width = df["W (um)"].iloc[int(0.5 * i)]
        length = df["L (um)"].iloc[int(0.5 * i)]

        if i in range(0, temp_range):
            temp = 25
        elif i in range(temp_range, 2 * temp_range):
            temp = -40
        else:
            temp = 125

        if "pfet" in device:
            if i == 0:
                idf = df[
                    [
                        "-vds (V)",
                        f"vgs ={mos_vgs[0]}.{i+1}",
                        f"vgs ={mos_vgs[1]}.{i+1}",
                        f"vgs ={mos_vgs[2]}.{i+1}",
                        f"vgs ={mos_vgs[3]}.{i+1}",
                        f"vgs ={mos_vgs[4]}.{i+1}",
                        f"vgs ={mos_vgs[5]}.{i+1}",
                    ]
                ].copy()

                idf.rename(
                    columns={
                        "-vds (V)": "vds",
                        f"vgs ={mos_vgs[0]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[0]}",
                        f"vgs ={mos_vgs[1]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[1]}",
                        f"vgs ={mos_vgs[2]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[2]}",
                        f"vgs ={mos_vgs[3]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[3]}",
                        f"vgs ={mos_vgs[4]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[4]}",
                        f"vgs ={mos_vgs[5]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[5]}",
                    },
                    inplace=True,
                )
            else:
                idf = df[
                    [
                        f"-vds (V).{i}",
                        f"vgs ={mos_vgs[0]}.{i+1}",
                        f"vgs ={mos_vgs[1]}.{i+1}",
                        f"vgs ={mos_vgs[2]}.{i+1}",
                        f"vgs ={mos_vgs[3]}.{i+1}",
                        f"vgs ={mos_vgs[4]}.{i+1}",
                        f"vgs ={mos_vgs[5]}.{i+1}",
                    ]
                ].copy()

                idf.rename(
                    columns={
                        f"-vds (V).{i}": "vds",
                        f"vgs ={mos_vgs[0]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[0]}",
                        f"vgs ={mos_vgs[1]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[1]}",
                        f"vgs ={mos_vgs[2]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[2]}",
                        f"vgs ={mos_vgs[3]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[3]}",
                        f"vgs ={mos_vgs[4]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[4]}",
                        f"vgs ={mos_vgs[5]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[5]}",
                    },
                    inplace=True,
                )
        else:
            if i == 0:
                idf = df[
                    [
                        "vds (V)",
                        f"vgs ={mos_vgs[0]}.{i+1}",
                        f"vgs ={mos_vgs[1]}.{i+1}",
                        f"vgs ={mos_vgs[2]}.{i+1}",
                        f"vgs ={mos_vgs[3]}.{i+1}",
                        f"vgs ={mos_vgs[4]}.{i+1}",
                        f"vgs ={mos_vgs[5]}.{i+1}",
                    ]
                ].copy()

                idf.rename(
                    columns={
                        "vds (V)": "vds",
                        f"vgs ={mos_vgs[0]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[0]}",
                        f"vgs ={mos_vgs[1]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[1]}",
                        f"vgs ={mos_vgs[2]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[2]}",
                        f"vgs ={mos_vgs[3]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[3]}",
                        f"vgs ={mos_vgs[4]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[4]}",
                        f"vgs ={mos_vgs[5]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[5]}",
                    },
                    inplace=True,
                )
            else:
                idf = df[
                    [
                        f"vds (V).{i}",
                        f"vgs ={mos_vgs[0]}.{i+1}",
                        f"vgs ={mos_vgs[1]}.{i+1}",
                        f"vgs ={mos_vgs[2]}.{i+1}",
                        f"vgs ={mos_vgs[3]}.{i+1}",
                        f"vgs ={mos_vgs[4]}.{i+1}",
                        f"vgs ={mos_vgs[5]}.{i+1}",
                    ]
                ].copy()

                idf.rename(
                    columns={
                        f"vds (V).{i}": "vds",
                        f"vgs ={mos_vgs[0]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[0]}",
                        f"vgs ={mos_vgs[1]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[1]}",
                        f"vgs ={mos_vgs[2]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[2]}",
                        f"vgs ={mos_vgs[3]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[3]}",
                        f"vgs ={mos_vgs[4]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[4]}",
                        f"vgs ={mos_vgs[5]}.{i+1}": f"measured_vgs{i+1} ={mos_vgs[5]}",
                    },
                    inplace=True,
                )

        idf["W (um)"] = width
        idf["L (um)"] = length
        idf["temp"] = temp

        idf.dropna(inplace=True)
        all_dfs.append(idf)

    dfs = pd.concat(all_dfs, axis=1)
    dfs.drop_duplicates(inplace=True)

    return dfs


def call_simulator(file_name: str) -> int:
    """
    Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    Returns:
        int: Return code of the simulation. 0 if success.  Non-zero if failed.
    """

    return os.system(f"ngspice -b -a {file_name} -o {file_name}.log > {file_name}.log")


def run_sim(dirpath: str, device: str, id_rds: str, width: float, length: float, temp=25) -> dict:
    """
    Run simulation at specific information and corner
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

    device1 = "nmos" if "nfet" in device else "pmos"

    if "pfet_03v3" in device:
        vgs = VGS_P03V3
        vds = VDS_P03V3
    elif "pfet_06v0" in device:
        vgs = VGS_P06V0
        vds = VDS_P06V0
    elif "nfet_06v0" in device and "nvt" not in device:
        vgs = VGS_N06V0
        vds = VDS_N06V0
    elif "nfet_06v0_nvt" in device:
        vgs = VGS_N06V0_N
        vds = VDS_N06V0_N
    else:
        vds = VDS_N03V3
        vgs = VGS_N03V3

    netlist_tmp = os.path.join(f"device_netlists_{id_rds}", f"{device1}.spice")

    info = {}
    info["device"] = device
    info["temp"] = temp
    info["length"] = length
    info["width"] = width

    width_str = width
    length_str = length
    temp_str = temp

    dev_netlists_path = os.path.join(dirpath, f"{device}_netlists_{id_rds}")
    os.makedirs(dev_netlists_path, exist_ok=True)

    sp_file_name = f"netlist_w{width_str}_l{length_str}_t{temp_str}.spice"
    netlist_path = os.path.join(dev_netlists_path, sp_file_name)

    sim_file_name = f"T{temp}_simulated_W{width_str}_L{length_str}.csv"
    result_path = os.path.join(dev_netlists_path, sim_file_name)

    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device,
                    width=width_str,
                    length=length_str,
                    temp=temp_str,
                    vds=vds,
                    vgs=vgs,
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

    info["mos_iv_simulated"] = mos_iv

    return info


def run_sims(
    df: pd.DataFrame, dirpath: str, device: str, id_rds, num_workers=mp.cpu_count()
) -> pd.DataFrame:
    """
    passing netlists to run_sim function
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

    loops = df["L (um)"].count()
    temp_range = int(loops / 3)
    df["temp"] = 25
    df["temp"][temp_range : 2 * temp_range] = -40
    df["temp"][2 * temp_range : 3 * temp_range] = 125

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures_list = []
        for j, row in df.iterrows():
            futures_list.append(
                executor.submit(
                    run_sim,
                    dirpath,
                    device,
                    id_rds,
                    row["W (um)"],
                    row["L (um)"],
                    row["temp"],
                )
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logging.info("Test case generated an exception: %s" % (exc))

    sf = glob.glob(f"{dirpath}/{device}_netlists_{id_rds}/*.csv")
    if "pfet_03v3" in device:
        mos_vgs = PMOS3P3_VGS
    elif "pfet_06v0" in device:
        mos_vgs = PMOS6P0_VGS
    elif "nfet_06v0" in device and "nvt" not in device:
        mos_vgs = NMOS6P0_VGS
    elif "nfet_06v0_nvt" in device:
        mos_vgs = NMOS6P0_VGS_N
    else:
        mos_vgs = MOS_VGS

    # sweeping on all generated cvs files
    for i in range(len(sf)):
        df = pd.read_csv(
            sf[i],
            delimiter=r"\s+",
        )

        if id_rds == "Id":
            v_gs = "v(G_tn)"
            i_vds = "-i(Vds)"

            if "pfet" in device:
                i_vds = "i(Vds)"

            sdf = df.pivot(index="v-sweep", columns=(v_gs), values=i_vds)

        else:
            # drop strange rows
            df.drop(df.loc[df["v-sweep"] == "v-sweep"].index, inplace=True)
            df = df.reset_index(drop=True)
            df = df.astype(float)

            # use the first column as index
            df = df.set_index("v-sweep")

            if device in ["nfet_06v0", "pfet_06v0", "nfet_06v0_dss", "pfet_06v0_dss"]:
                # reciprocal the column values
                df["Rds"] = df["Rds"].apply(np.reciprocal)
            v_gs = "Vg"
            i_vds = "Rds"
            sdf = df.pivot(columns=(v_gs), values=i_vds)

        # Writing final simulated data 1
        sdf.rename(
            columns={
                mos_vgs[0]: f"simulated_vgs={mos_vgs[0]}",
                mos_vgs[1]: f"simulated_vgs={mos_vgs[1]}",
                mos_vgs[2]: f"simulated_vgs={mos_vgs[2]}",
                mos_vgs[3]: f"simulated_vgs={mos_vgs[3]}",
                mos_vgs[4]: f"simulated_vgs={mos_vgs[4]}",
                mos_vgs[5]: f"simulated_vgs={mos_vgs[5]}",
            },
            inplace=True,
        )
        if "pfet" in device:
            # reverse the rows
            sdf = sdf.iloc[::-1]

        sdf.to_csv(sf[i], index=True, header=True, sep=",")
    df = pd.DataFrame(results)
    return df


def error_cal(
    df: pd.DataFrame,
    sim_df: pd.DataFrame,
    meas_df: pd.DataFrame,
    dev_path: str,
    device: str,
    id_rds: str,
) -> None:
    """
    error function calculates the error between measured, simulated data

    Args:
        df(pd.DataFrame): Dataframe contains devices and csv files
                          which represent measured, simulated data
        sim_df(pd.DataFrame): Dataframe contains devices and csv files simulated
        meas_df(pd.DataFrame): Dataframe contains devices and csv files measured
        dev_path(str): The path in which we write data
        id_rds(str): select id or rds

    """

    id_rd = 1 if id_rds == "Rds" else 0

    # adding error columns to the merged dataframe
    merged_dfs = list()
    loops = df["L (um)"].count()
    temp_range = int(loops / 3)
    df["temp"] = 25
    df["temp"][temp_range : 2 * temp_range] = -40
    df["temp"][2 * temp_range : 3 * temp_range] = 125

    if "pfet_03v3" in device:
        mos_vgs = PMOS3P3_VGS
    elif "pfet_06v0" in device:
        mos_vgs = PMOS6P0_VGS
    elif "nfet_06v0" in device and "nvt" not in device:
        mos_vgs = NMOS6P0_VGS
    elif "nfet_06v0_nvt" in device:
        mos_vgs = NMOS6P0_VGS_N
    else:
        mos_vgs = MOS_VGS

    # create a new dataframe for rms error
    rms_df = pd.DataFrame(columns=["temp", "W (um)", "L (um)", "rms_error"])

    for i in range(len(sim_df)):
        length = df["L (um)"].iloc[int(i)]
        w = df["W (um)"].iloc[int(i)]
        t = df["temp"].iloc[int(i)]

        sim_file_name = f"T{t}_simulated_W{w}_L{length}.csv"
        sim_path = os.path.join("mos_iv_regr", device, f"{device}_netlists_{id_rds}", sim_file_name)

        simulated_data = pd.read_csv(sim_path)

        measured_data = meas_df[
            [
                f"measured_vgs{2*i+id_rd} ={mos_vgs[0]}",
                f"measured_vgs{2*i+id_rd} ={mos_vgs[1]}",
                f"measured_vgs{2*i+id_rd} ={mos_vgs[2]}",
                f"measured_vgs{2*i+id_rd} ={mos_vgs[3]}",
                f"measured_vgs{2*i+id_rd} ={mos_vgs[4]}",
                f"measured_vgs{2*i+id_rd} ={mos_vgs[5]}",
            ]
        ].copy()

        measured_data.rename(
            columns={
                f"measured_vgs{2*i+id_rd} ={mos_vgs[0]}": f"measured_vgs={mos_vgs[0]}",
                f"measured_vgs{2*i+id_rd} ={mos_vgs[1]}": f"measured_vgs={mos_vgs[1]}",
                f"measured_vgs{2*i+id_rd} ={mos_vgs[2]}": f"measured_vgs={mos_vgs[2]}",
                f"measured_vgs{2*i+id_rd} ={mos_vgs[3]}": f"measured_vgs={mos_vgs[3]}",
                f"measured_vgs{2*i+id_rd} ={mos_vgs[4]}": f"measured_vgs={mos_vgs[4]}",
                f"measured_vgs{2*i+id_rd} ={mos_vgs[5]}": f"measured_vgs={mos_vgs[5]}",
            },
            inplace=True,
        )
        measured_data["v-sweep"] = simulated_data["v-sweep"]
        result_data = simulated_data.merge(measured_data, how="left")

        if id_rds == "Id":
            # clipping all the  values to lowest_curr
            lowest_curr = 5e-12
            result_data[f"measured_vgs={mos_vgs[0]}"] = result_data[f"measured_vgs={mos_vgs[0]}"].clip(
                lower=lowest_curr
            )
            result_data[f"measured_vgs={mos_vgs[1]}"] = result_data[f"measured_vgs={mos_vgs[1]}"].clip(
                lower=lowest_curr
            )
            result_data[f"measured_vgs={mos_vgs[2]}"] = result_data[f"measured_vgs={mos_vgs[2]}"].clip(
                lower=lowest_curr
            )
            result_data[f"measured_vgs={mos_vgs[3]}"] = result_data[f"measured_vgs={mos_vgs[3]}"].clip(
                lower=lowest_curr
            )
            result_data[f"measured_vgs={mos_vgs[4]}"] = result_data[f"measured_vgs={mos_vgs[4]}"].clip(
                lower=lowest_curr
            )
            result_data[f"measured_vgs={mos_vgs[5]}"] = result_data[f"measured_vgs={mos_vgs[5]}"].clip(
                lower=lowest_curr
            )
            result_data[f"simulated_vgs={mos_vgs[0]}"] = result_data[f"simulated_vgs={mos_vgs[0]}"].clip(lower=lowest_curr)
            result_data[f"simulated_vgs={mos_vgs[1]}"] = result_data[f"simulated_vgs={mos_vgs[1]}"].clip(lower=lowest_curr)
            result_data[f"simulated_vgs={mos_vgs[2]}"] = result_data[f"simulated_vgs={mos_vgs[2]}"].clip(lower=lowest_curr)
            result_data[f"simulated_vgs={mos_vgs[3]}"] = result_data[f"simulated_vgs={mos_vgs[3]}"].clip(lower=lowest_curr)
            result_data[f"simulated_vgs={mos_vgs[4]}"] = result_data[f"simulated_vgs={mos_vgs[4]}"].clip(lower=lowest_curr)
            result_data[f"simulated_vgs={mos_vgs[5]}"] = result_data[f"simulated_vgs={mos_vgs[5]}"].clip(lower=lowest_curr)

        # Error calc
        result_data[f"err_vgs={mos_vgs[0]}"] = (
            np.abs(result_data[f"measured_vgs={mos_vgs[0]}"] - result_data[f"simulated_vgs={mos_vgs[0]}"])
            * 100.0
            / (result_data[f"measured_vgs={mos_vgs[0]}"])
        )
        result_data[f"err_vgs={mos_vgs[1]}"] = (
            np.abs(result_data[f"measured_vgs={mos_vgs[1]}"] - result_data[f"simulated_vgs={mos_vgs[1]}"])
            * 100.0
            / (result_data[f"measured_vgs={mos_vgs[1]}"])
        )
        result_data[f"err_vgs={mos_vgs[2]}"] = (
            np.abs(result_data[f"measured_vgs={mos_vgs[2]}"] - result_data[f"simulated_vgs={mos_vgs[2]}"])
            * 100.0
            / (result_data[f"measured_vgs={mos_vgs[2]}"])
        )
        result_data[f"err_vgs={mos_vgs[3]}"] = (
            np.abs(result_data[f"measured_vgs={mos_vgs[3]}"] - result_data[f"simulated_vgs={mos_vgs[3]}"])
            * 100.0
            / (result_data[f"measured_vgs={mos_vgs[3]}"])
        )
        result_data[f"err_vgs={mos_vgs[4]}"] = (
            np.abs(result_data[f"measured_vgs={mos_vgs[4]}"] - result_data[f"simulated_vgs={mos_vgs[4]}"])
            * 100.0
            / (result_data[f"measured_vgs={mos_vgs[4]}"])
        )
        result_data[f"err_vgs={mos_vgs[5]}"] = (
            np.abs(result_data[f"measured_vgs={mos_vgs[5]}"] - result_data[f"simulated_vgs={mos_vgs[5]}"])
            * 100.0
            / (result_data[f"measured_vgs={mos_vgs[5]}"])
        )
        result_data["length"] = length
        result_data["width"] = w
        result_data["temp"] = t

        # fill nan values with 0
        result_data.fillna(0, inplace=True)
        result_data["error"] = (
            np.abs(
                result_data[f"err_vgs={mos_vgs[0]}"]
                + result_data[f"err_vgs={mos_vgs[1]}"]
                + result_data[f"err_vgs={mos_vgs[2]}"]
                + result_data[f"err_vgs={mos_vgs[3]}"]
                + result_data[f"err_vgs={mos_vgs[4]}"]
                + result_data[f"err_vgs={mos_vgs[5]}"]
            )
            / 6
        )

        # Drop last voltage row as its derivative for Rds is high [No points after it]
        result_data = result_data.iloc[:-1, :]

        # get rms error
        result_data["rms_error"] = np.sqrt(np.mean(result_data["error"] ** 2))
        # fill rms dataframe
        rms_df.loc[i] = [t, w, length, result_data["rms_error"].iloc[0]]

        merged_dfs.append(result_data)
        merged_out = pd.concat(merged_dfs)

        merged_out.fillna(0, inplace=True)
        err_analysis_path = os.path.join(dev_path, f"error_analysis_{id_rds}.csv")
        merged_out.to_csv(err_analysis_path, index=False)

        rmse_path = os.path.join(dev_path, f"final_error_analysis_{id_rds}.csv")
        rms_df.to_csv(rmse_path, index=False)

    return None


def main():
    """
    Main function applies all regression vds_steps
    """

    ## Check ngspice version
    check_ngspice_version()

    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)
    pd.options.mode.chained_assignment = None

    main_regr_dir = "mos_iv_regr"

    devices = [
        "nfet_03v3",
        "pfet_03v3",
        "nfet_06v0",
        "pfet_06v0",
        "nfet_06v0_nvt",
        "nfet_03v3_dss",
        "pfet_03v3_dss",
        "nfet_06v0_dss",
        "pfet_06v0_dss",
    ]

    for dev in devices:
        dev_path = os.path.join(main_regr_dir, dev)

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(dev_path, exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {dev}")

        data_files = glob.glob(f"../../180MCU_SPICE_DATA/MOS/{dev}_iv.nl_out.xlsx")

        if len(data_files) < 1:
            logging.info(f"# Can't find file for device: {dev}")
            file = ""
        else:
            file = os.path.abspath(data_files[0])

        logging.info(f"#  data points file : {file}")

        if file != "":
            meas_df = ext_measured(dev_path, file, dev)
        else:
            meas_df = []

        # Get W, L from meas data
        meas_data_path = os.path.join(dev_path, f"{dev}.csv")
        df_meas = pd.read_csv(meas_data_path)
        df_meas_s = df_meas[["L (um)", "W (um)"]].copy()
        df_meas_s.dropna(inplace=True)

        sim_df_id = run_sims(df_meas_s, dev_path, dev, "Id")
        sim_df_rds = run_sims(df_meas_s, dev_path, dev, "Rds")

        logging.info(
            f"# Device {dev} number of measured_datapoints for Id : {len(sim_df_id) * len(meas_df)}"
        )

        logging.info(
            f"# Device {dev} number of simulated datapoints for Id : {len(sim_df_id) * len(meas_df)} "
        )

        logging.info(
            f"# Device {dev} number of measured_datapoints for Rds : {len(sim_df_rds) * len(meas_df)}"
        )
        logging.info(
            f"# Device {dev} number of simulated datapoints for Rds : {len(sim_df_rds) * len(meas_df)}"
        )

        # passing dataframe to the error_calculation function
        # calling error function for creating statistical csv file
        error_cal(df_meas_s, sim_df_id, meas_df, dev_path, dev, "Id")
        error_cal(df_meas_s, sim_df_id, meas_df, dev_path, dev, "Rds")

        # reading from the csv file contains all error data
        # merged_all contains all simulated, measured, error data
        for sim in ["Id", "Rds"]:
            merged_all = pd.read_csv(f"{dev_path}/final_error_analysis_{sim}.csv")

            # calculating the error of each device and reporting it
            min_error_total = float(merged_all["rms_error"].min())
            max_error_total = float(merged_all["rms_error"].max())
            mean_error_total = float(merged_all["rms_error"].mean())

            # Cliping rmse at 100%
            min_error_total = 100 if min_error_total > 100 else min_error_total
            max_error_total = 100 if max_error_total > 100 else max_error_total
            mean_error_total = 100 if mean_error_total > 100 else mean_error_total

            # logging rmse
            logging.info(
                f"# Device {dev} {sim} min error: {min_error_total:.2f}%, max error: {max_error_total:.2f}%, mean error {mean_error_total:.2f}%"
            )

            # Verify regression results
            if mean_error_total <= PASS_THRESH:
                logging.info(f"# Device {dev} {sim} has passed regression.")
            else:
                logging.error(
                    f"# Device {dev} {sim} has failed regression. Needs more analysis."
                )
                logging.error(
                    "#Failed regression for MOS-iv-vgs analysis."
                )
                exit(1)


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
