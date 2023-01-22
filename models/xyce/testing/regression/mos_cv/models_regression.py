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

pd.options.mode.chained_assignment = None  # default='warn'
# constants
PASS_THRESH = 2.0

MOS = [0, -0.825, -1.65, -2.475, -3.3]
PMOS3P3_VPS = ["-0", 0.825, 1.65, 2.475, 3.3]
NMOS6P0_VPS = [0, -1, -2, -3]
PMOS6P0_VPS = ["-0", 1, 2, 3]

MOS1 = [0, 1.1, 2.2, 3.3]
PMOS3P3_VPS1 = ["-0", -1.1, -2.2, -3.3]
NMOS6P0_VPS1 = [0, 2, 4, 6]
PMOS6P0_VPS1 = ["-0", -2, -4, -6]
# #######################
VBS_N03V3C = "0 -3.3 -0.825"
VBS_P03V3C = "0 3.3 0.825"
VBS_N06V0C = "0 -3 -1"
VBS_P06V0C = "0 3 1"
VBS_N06V0_NC = "0 -3 -1"

VGS_N03V3C = "-3.3 3.3 0.1"
VGS_P03V3C = "-3.3 3.3 0.1"
VGS_N06V0C = "-6 6 0.1"
VGS_P06V0C = "-6 6 0.1"
VGS_N06V0_NC = "-6 6 0.1"

VGS_N03V3D = "0 3.4 1.1"
VGS_P03V3D = "0 -3.4 -1.1"
VGS_N06V0D = "0 6 2"
VGS_P06V0D = "0 -6 -2"
VGS_N06V0_ND = "0 6 2"

VDS_N03V3D = "0 3.3 0.1"
VDS_P03V3D = "0 -3.3 -0.1"
VDS_N06V0D = "0 6 0.1"
VDS_P06V0D = "0 -6 -0.1"
VDS_N06V0_ND = "0 6 0.1"


def ext_measured(dev_data_path: str, device: str) -> pd.DataFrame:
    """Extracting the measured data of  devices from excel sheet

    Args:
         dev_data_path(str): path to the data sheet
         devices(str):  undertest device

    Returns:
         dfs(pd.DataFrame): A data frame contains all extracted data

    """

    # Read Data
    read_file = pd.read_excel(dev_data_path)
    read_file.to_csv(f"mos_cv_regr/{device}/{device}.csv", index=False, header=True)

    df = pd.read_csv(f"mos_cv_regr/{device}/{device}.csv")
    loops = int(0.5 * df["L (um)"].count())
    all_dfs1 = []
    all_dfs2 = []
    all_dfs3 = []

    if device == "pfet_03v3" or device == "pfet_03v3_dss":
        mos = PMOS3P3_VPS
        mos1 = PMOS3P3_VPS1
    elif device == "pfet_06v0" or device == "pfet_06v0_dss":
        mos = PMOS6P0_VPS
        mos1 = PMOS6P0_VPS1
    elif device == "nfet_06v0" or device == "nfet_06v0_dss":
        mos = NMOS6P0_VPS
        mos1 = NMOS6P0_VPS1
    elif device == "nfet_06v0_nvt":
        mos = NMOS6P0_VPS
        mos1 = NMOS6P0_VPS1
    else:
        mos = MOS
        mos1 = MOS1

    vgs = "Vgs (V)"
    vds = "Vds (V)"
    if device in ["pfet_03v3", "pfet_06v0", "pfet_03v3_dss", "pfet_06v0_dss"]:
        vgs = "-Vgs (V)"
        vds = "-Vds (V)"
    for i in range(loops):
        width = df["W (um)"].iloc[i]
        length = df["L (um)"].iloc[i]

        if i == 0:

            if device in ["nfet_03v3", "pfet_03v3", "nfet_03v3_dss", "pfet_03v3_dss"]:
                idf1 = df[
                    [
                        vgs,
                        f"Vbs={mos[0]}",
                        f"Vbs={mos[1]}",
                        f"Vbs={mos[2]}",
                        f"Vbs={mos[3]}",
                        f"Vbs={mos[4]}",
                    ]
                ].copy()

                idf1.rename(
                    columns={
                        vgs: "vgs",
                        f"Vbs={mos[0]}": f"measured_vbs{i}={mos[0]}",
                        f"Vbs={mos[1]}": f"measured_vbs{i}={mos[1]}",
                        f"Vbs={mos[2]}": f"measured_vbs{i}={mos[2]}",
                        f"Vbs={mos[3]}": f"measured_vbs{i}={mos[3]}",
                        f"Vbs={mos[4]}": f"measured_vbs{i}={mos[4]}",
                    },
                    inplace=True,
                )
            else:
                idf1 = df[
                    [
                        vgs,
                        f"Vbs={mos[0]}",
                        f"Vbs={mos[1]}",
                        f"Vbs={mos[2]}",
                        f"Vbs={mos[3]}",
                    ]
                ].copy()

                idf1.rename(
                    columns={
                        vgs: "vgs",
                        f"Vbs={mos[0]}": f"measured_vbs{i}={mos[0]}",
                        f"Vbs={mos[1]}": f"measured_vbs{i}={mos[1]}",
                        f"Vbs={mos[2]}": f"measured_vbs{i}={mos[2]}",
                        f"Vbs={mos[3]}": f"measured_vbs{i}={mos[3]}",
                    },
                    inplace=True,
                )
            idf2 = df[
                [
                    vds,
                    f"Vgs={mos1[0]}",
                    f"Vgs={mos1[1]}",
                    f"Vgs={mos1[2]}",
                    f"Vgs={mos1[3]}",
                ]
            ].copy()

            idf2.rename(
                columns={
                    vds: "vds",
                    f"Vgs={mos1[0]}": f"measured_vgs{i}={mos1[0]}",
                    f"Vgs={mos1[1]}": f"measured_vgs{i}={mos1[1]}",
                    f"Vgs={mos1[2]}": f"measured_vgs{i}={mos1[2]}",
                    f"Vgs={mos1[3]}": f"measured_vgs{i}={mos1[3]}",
                },
                inplace=True,
            )
            idf3 = df[
                [
                    vds,
                    f"Vgs={mos1[0]}.{i+1}",
                    f"Vgs={mos1[1]}.{i+1}",
                    f"Vgs={mos1[2]}.{i+1}",
                    f"Vgs={mos1[3]}.{i+1}",
                ]
            ].copy()

            idf3.rename(
                columns={
                    vds: "vds",
                    f"Vgs={mos1[0]}.{i+1}": f"measured_vgs{i}={mos1[0]}",
                    f"Vgs={mos1[1]}.{i+1}": f"measured_vgs{i}={mos1[1]}",
                    f"Vgs={mos1[2]}.{i+1}": f"measured_vgs{i}={mos1[2]}",
                    f"Vgs={mos1[3]}.{i+1}": f"measured_vgs{i}={mos1[3]}",
                },
                inplace=True,
            )
        else:

            if device in ["nfet_03v3", "pfet_03v3", "nfet_03v3_dss", "pfet_03v3_dss"]:
                idf1 = df[
                    [
                        vgs,
                        f"Vbs={mos[0]}.{i}",
                        f"Vbs={mos[1]}.{i}",
                        f"Vbs={mos[2]}.{i}",
                        f"Vbs={mos[3]}.{i}",
                        f"Vbs={mos[4]}.{i}",
                    ]
                ].copy()

                idf1.rename(
                    columns={
                        vgs: "vgs",
                        f"Vbs={mos[0]}.{i}": f"measured_vbs{i}={mos[0]}",
                        f"Vbs={mos[1]}.{i}": f"measured_vbs{i}={mos[1]}",
                        f"Vbs={mos[2]}.{i}": f"measured_vbs{i}={mos[2]}",
                        f"Vbs={mos[3]}.{i}": f"measured_vbs{i}={mos[3]}",
                        f"Vbs={mos[4]}.{i}": f"measured_vbs{i}={mos[4]}",
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
                        f"Vbs={mos[3]}.{i}",
                    ]
                ].copy()

                idf1.rename(
                    columns={
                        vgs: "vgs",
                        f"Vbs={mos[0]}.{i}": f"measured_vbs{i}={mos[0]}",
                        f"Vbs={mos[1]}.{i}": f"measured_vbs{i}={mos[1]}",
                        f"Vbs={mos[2]}.{i}": f"measured_vbs{i}={mos[2]}",
                        f"Vbs={mos[3]}.{i}": f"measured_vbs{i}={mos[3]}",
                    },
                    inplace=True,
                )
            idf2 = df[
                [
                    vds,
                    f"Vgs={mos1[0]}.{2*i}",
                    f"Vgs={mos1[1]}.{2*i}",
                    f"Vgs={mos1[2]}.{2*i}",
                    f"Vgs={mos1[3]}.{2*i}",
                ]
            ].copy()

            idf2.rename(
                columns={
                    vds: "vds",
                    f"Vgs={mos1[0]}.{2*i}": f"measured_vgs{i}={mos1[0]}",
                    f"Vgs={mos1[1]}.{2*i}": f"measured_vgs{i}={mos1[1]}",
                    f"Vgs={mos1[2]}.{2*i}": f"measured_vgs{i}={mos1[2]}",
                    f"Vgs={mos1[3]}.{2*i}": f"measured_vgs{i}={mos1[3]}",
                },
                inplace=True,
            )
            idf3 = df[
                [
                    vds,
                    f"Vgs={mos1[0]}.{2*i + 1}",
                    f"Vgs={mos1[1]}.{2*i + 1}",
                    f"Vgs={mos1[2]}.{2*i + 1}",
                    f"Vgs={mos1[3]}.{2*i + 1}",
                ]
            ].copy()

            idf3.rename(
                columns={
                    vds: "vds",
                    f"Vgs={mos1[0]}.{2*i + 1}": f"measured_vgs{i}={mos1[0]}",
                    f"Vgs={mos1[1]}.{2*i + 1}": f"measured_vgs{i}={mos1[1]}",
                    f"Vgs={mos1[2]}.{2*i + 1}": f"measured_vgs{i}={mos1[2]}",
                    f"Vgs={mos1[3]}.{2*i + 1}": f"measured_vgs{i}={mos1[3]}",
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
    return dfs1, dfs2, dfs3


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    log_file = file_name.replace("-hspice-ext all ", "")
    os.system(f"Xyce {file_name} -l {log_file}.log 2> /dev/null")


def run_sim(dirpath: str, device: str, width: float, length: float, nf: float) -> dict:
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

    vbsc = VBS_N03V3C
    vdsd = VDS_N03V3D
    vgsc = VGS_N03V3C
    vgsd = VGS_N03V3D
    if device == "pfet_03v3" or device == "pfet_03v3_dss":
        vbsc = VBS_P03V3C
        vdsd = VDS_P03V3D
        vgsc = VGS_P03V3C
        vgsd = VGS_P03V3D
    elif device == "pfet_06v0" or device == "pfet_06v0_dss":
        vbsc = VBS_P06V0C
        vdsd = VDS_P06V0D
        vgsc = VGS_P06V0C
        vgsd = VGS_P06V0D
    elif device == "nfet_06v0" or device == "nfet_06v0_dss":
        vbsc = VBS_N06V0C
        vdsd = VDS_N06V0D
        vgsc = VGS_N06V0C
        vgsd = VGS_N06V0D
    elif device == "nfet_06v0_nvt":
        vbsc = VBS_N06V0C
        vdsd = VDS_N06V0D
        vgsc = VGS_N06V0C
        vgsd = VGS_N06V0D
    caps = ["c", "d", "s"]
    for cap in caps:
        netlist_tmp = f"device_netlists_Cg{cap}/mos.spice"

        info = {}
        info["device"] = device
        info["length"] = length
        info["width"] = width
        width_str = width
        length_str = length
        nf_str = nf
        if cap == "c":
            vgs = vgsc
            vds = vdsd
            vbs = vbsc
        else:
            vgs = vgsd
            vds = vdsd
            vbs = vbsc

        s = f"netlist_w{width_str}_l{length_str}.spice"
        netlist_path = f"{dirpath}/{device}_netlists_Cg{cap}/{s}"
        s = f"simulated_W{width_str}_L{length_str}.csv"
        result_path = f"{dirpath}/{device}_netlists_Cg{cap}/{s}"
        with open(netlist_tmp) as f:
            tmpl = Template(f.read())
            os.makedirs(f"{dirpath}/{device}_netlists_Cg{cap}", exist_ok=True)
            with open(netlist_path, "w") as netlist:
                netlist.write(
                    tmpl.render(
                        width=width_str,
                        length=length_str,
                        nf=nf_str,
                        vgs=vgs,
                        vds=vds,
                        vbs=vbs,
                        device=device,
                        AD=float(width_str) * 0.24,
                        PD=2 * (float(width_str) + 0.24),
                        AS=float(width_str) * 0.24,
                        PS=2 * (float(width_str) + 0.24),
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


def run_sims(df: pd.DataFrame, dirpath: str, device: str, num_workers=mp.cpu_count()) -> pd.DataFrame:
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures_list = []
        for j, row in df.iterrows():
            futures_list.append(
                executor.submit(
                    run_sim, dirpath, device, row["W (um)"], row["L (um)"], row["nf"]
                )
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logging.info(f"Test case generated an exception: {exc}")

    caps = ["c", "d", "s"]
    for cap in caps:
        sf = glob.glob(f"{dirpath}/{device}_netlists_Cg{cap}/*.csv")
        if cap == "c":
            if device == "pfet_03v3" or device == "pfet_03v3_dss":
                mos = PMOS3P3_VPS
            elif device == "pfet_06v0" or device == "pfet_06v0_dss":
                mos = PMOS6P0_VPS
            elif (
                device == "nfet_06v0"
                or device == "nfet_06v0_dss"
                or device == "nfet_06v0_nvt"
            ):
                mos = NMOS6P0_VPS
            else:
                mos = MOS
        else:
            if device == "pfet_03v3" or device == "pfet_03v3_dss":
                mos = PMOS3P3_VPS1
            elif device == "pfet_06v0" or device == "pfet_06v0_dss":
                mos = PMOS6P0_VPS1
            elif (
                device == "nfet_06v0"
                or device == "nfet_06v0_dss"
                or device == "nfet_06v0_nvt"
            ):
                mos = NMOS6P0_VPS1
            else:
                mos = MOS1

        # sweeping on all generated cvs files
        for i in range(len(sf)):
            df = pd.read_csv(sf[i])
 
            if cap == "c":
                # use the first column as index
                v_s = "V(S_TN)"
                i_vds = "{-1.0E15*N(XMN1:M0:CGS) - 1.0E15*N(XMN1:M0:CGD)}"
                v1 = "V(G_TN)"
                # drop time column
                df.drop(df.columns[0], axis=1, inplace=True)
                # drop duplicate rows for columns V(S_TN) and V(G_TN)
                df.drop_duplicates(subset=["V(S_TN)", "V(G_TN)"], inplace=True)
                sdf = df.pivot(index=v1, columns=(v_s), values=i_vds)
                # Writing final simulated data 1
                sdf.rename(
                    columns={
                        0: "vb1",
                        mos[1]: "vb2",
                        mos[2]: "vb3",
                        mos[3]: "vb4",
                    },
                    inplace=True,
                )
                if len(mos) == 5:
                    sdf.rename(
                        columns={
                            mos[4]: "vb5",
                        },
                        inplace=True,
                    )
            elif cap == "d":
                # drop time column
                df.drop(df.columns[0], axis=1, inplace=True)
                # drop duplicate rows for columns V(S_TN) and V(G_TN)
                df.drop_duplicates(subset=["V(D_TN)", "V(G_TN)"], inplace=True)                
                # use the first column as index
                v_s = "V(G_TN)"
                i_vds = "{-1.0E15*N(XMN1:M0:CGD)}"
                v1 = "V(D_TN)"
                sdf = df.pivot(index=v1, columns=(v_s), values=i_vds)

                # Writing final simulated data 1
                sdf.rename(
                    columns={0: "vgs1", mos[1]: "vgs2", mos[2]: "vgs3", mos[3]: "vgs4"},
                    inplace=True,
                )
            else:
                # drop time column
                df.drop(df.columns[0], axis=1, inplace=True)
                # drop duplicate rows for columns V(S_TN) and V(G_TN)
                df.drop_duplicates(subset=["V(D_TN)", "V(G_TN)"], inplace=True)                
                # use the first column as index
                v_s = "V(G_TN)"
                i_vds = "{-1.0E15*N(XMN1:M0:CGS)}"
                v1 = "V(D_TN)"
                sdf = df.pivot(index=v1, columns=(v_s), values=i_vds)

                # Writing final simulated data 1
                sdf.rename(
                    columns={0: "vgs1", mos[1]: "vgs2", mos[2]: "vgs3", mos[3]: "vgs4"},
                    inplace=True,
                )
            if device[0] == "p":
                # reverse the rows
                sdf = sdf.iloc[::-1]
            sdf.to_csv(sf[i], index=True, header=True, sep=",")

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
    if device == "pfet_03v3" or device == "pfet_03v3_dss":
        mos = PMOS3P3_VPS
        mos1 = PMOS3P3_VPS1
    elif device == "pfet_06v0" or device == "pfet_06v0_dss":
        mos = PMOS6P0_VPS
        mos1 = PMOS6P0_VPS1
    elif device == "nfet_06v0" or device == "nfet_06v0_dss":
        mos = NMOS6P0_VPS
        mos1 = NMOS6P0_VPS1
    elif device == "nfet_06v0_nvt":
        mos = NMOS6P0_VPS
        mos1 = NMOS6P0_VPS1
    else:
        mos = MOS
        mos1 = MOS1
    caps = ["c", "s", "d"]

    # create a new dataframe for rms error
    rms_df = pd.DataFrame(columns=["temp", "W (um)", "L (um)", "rms_error"])
    for cap in caps:
        merged_dfs = list()
        if cap == "c":
            meas_df = meas_df1
        elif cap == "s":
            meas_df = meas_df2
        else:
            meas_df = meas_df3

        for i in range(len(sim_df)):
            length = df["L (um)"].iloc[int(i)]
            w = df["W (um)"].iloc[int(i)]
            s = f"simulated_W{w}_L{length}.csv"
            sim_path = f"mos_cv_regr/{device}/{device}_netlists_Cg{cap}/{s}"
            if w == "200":
                continue
            simulated_data = pd.read_csv(sim_path)

            if cap == "c":
                if device in [
                    "nfet_03v3",
                    "pfet_03v3",
                    "nfet_03v3_dss",
                    "pfet_03v3_dss",
                ]:
                    measured_data = meas_df[
                        [
                            f"measured_vbs{i}={mos[0]}",
                            f"measured_vbs{i}={mos[1]}",
                            f"measured_vbs{i}={mos[2]}",
                            f"measured_vbs{i}={mos[3]}",
                            f"measured_vbs{i}={mos[4]}",
                        ]
                    ].copy()
                    measured_data.rename(
                        columns={
                            f"measured_vbs{i}={mos[0]}": "measured_v1",
                            f"measured_vbs{i}={mos[1]}": "measured_v2",
                            f"measured_vbs{i}={mos[2]}": "measured_v3",
                            f"measured_vbs{i}={mos[3]}": "measured_v4",
                            f"measured_vbs{i}={mos[4]}": "measured_v5",
                        },
                        inplace=True,
                    )
                else:

                    measured_data = meas_df[
                        [
                            f"measured_vbs{i}={mos[0]}",
                            f"measured_vbs{i}={mos[1]}",
                            f"measured_vbs{i}={mos[2]}",
                            f"measured_vbs{i}={mos[3]}",
                        ]
                    ].copy()
                    measured_data.rename(
                        columns={
                            f"measured_vbs{i}={mos[0]}": "measured_v1",
                            f"measured_vbs{i}={mos[1]}": "measured_v2",
                            f"measured_vbs{i}={mos[2]}": "measured_v3",
                            f"measured_vbs{i}={mos[3]}": "measured_v4",
                        },
                        inplace=True,
                    )
                measured_data["V(G_TN)"] = simulated_data["V(G_TN)"]
                result_data = simulated_data.merge(measured_data, how="left")

            else:
                measured_data = meas_df[
                    [
                        f"measured_vgs{i}={mos1[0]}",
                        f"measured_vgs{i}={mos1[1]}",
                        f"measured_vgs{i}={mos1[2]}",
                        f"measured_vgs{i}={mos1[3]}",
                    ]
                ].copy()
                measured_data.rename(
                    columns={
                        f"measured_vgs{i}={mos1[0]}": "measured_v1",
                        f"measured_vgs{i}={mos1[1]}": "measured_v2",
                        f"measured_vgs{i}={mos1[2]}": "measured_v3",
                        f"measured_vgs{i}={mos1[3]}": "measured_v4",
                    },
                    inplace=True,
                )

                measured_data["V(D_TN)"] = simulated_data["V(D_TN)"]
                result_data = simulated_data.merge(measured_data, how="left")

            if cap == "c":

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
                if device in [
                    "nfet_03v3",
                    "pfet_03v3",
                    "nfet_03v3_dss",
                    "pfet_03v3_dss",
                ]:
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
            result_data["length"] = length
            result_data["width"] = w
            result_data["temp"] = 25.0
            # fill nan values with 0
            result_data.fillna(0, inplace=True)
            result_data["rms_error"] = np.sqrt(np.mean(result_data["error"] ** 2))
            # fill rms dataframe
            rms_df.loc[i] = [25.0, w, length, result_data["rms_error"].iloc[0]]

            merged_dfs.append(result_data)
            merged_out = pd.concat(merged_dfs)
            merged_out.fillna(0, inplace=True)
            merged_out.to_csv(f"{dev_path}/error_analysis_Cg{cap}.csv", index=False)
            rms_df.to_csv(f"{dev_path}/finalerror_analysis_Cg{cap}.csv", index=False)

    return None


def main():
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

    main_regr_dir = "mos_cv_regr"

    devices = [
        "nfet_03v3",
        "pfet_03v3",
        "nfet_06v0",
        "pfet_06v0",
        "nfet_03v3_dss",
        "pfet_03v3_dss",
        "nfet_06v0_dss",
        "pfet_06v0_dss",
        "nfet_06v0_nvt",
    ]
    measured_data = ["3p3_cv", "6p0_cv", "3p3_sab_cv", "6p0_sab_cv", "6p0_nat_cv"]
    if os.path.exists(main_regr_dir) and os.path.isdir(main_regr_dir):
        shutil.rmtree(main_regr_dir)

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        os.makedirs(f"{dev_path}", exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {dev}")

        data_files = glob.glob(
            f"../../180MCU_SPICE_DATA/MOS/{measured_data[int(i*0.5)]}.nl_out.xlsx"
        )
        if len(data_files) < 1:
            logging.erorr(f"# Can't find file for device: {dev}")
            file = ""
        else:
            file = os.path.abspath(data_files[0])
        logging.info(f"#  data points file : {file}")

        if file != "":
            meas_df1, meas_df2, meas_df3 = ext_measured(file, dev)
        else:
            meas_df1 = []
            meas_df2 = []
            meas_df3 = []

        df1 = pd.read_csv(f"mos_cv_regr/{dev}/{dev}.csv")
        df2 = df1[["L (um)", "W (um)"]].copy()
        df2.dropna(inplace=True)
        loops = int(0.5 * df2["L (um)"].count())
        df = df2[["L (um)", "W (um)"]].iloc[0:loops]
        sim_df_id = run_sims(df, dev_path, dev)

        logging.info(
            f"# Device {dev} number of measured_datapoints for cv : {len(sim_df_id) * (len(meas_df1) + len(meas_df2) + len(meas_df3))}",
        )
        logging.info(
            f"# Device {dev} number of simulated datapoints for cv : { len(sim_df_id) * (len(meas_df1) + len(meas_df2) + len(meas_df3))}",
        )

        # passing dataframe to the error_calculation function
        # calling error function for creating statistical csv file

        error_cal(df, sim_df_id, meas_df1, meas_df2, meas_df3, dev_path, dev)

        caps = ["c", "d", "s"]

        for cap in caps:
            # reading from the csv file contains all error data
            # merged_all contains all simulated, measured, error data
            merged_all = pd.read_csv(f"{dev_path}/finalerror_analysis_Cg{cap}.csv")

            # calculating the error of each device and reporting it
            min_error_total = float()
            max_error_total = float()
            mean_error_total = float()
            min_error_total = merged_all["rms_error"].min()
            max_error_total = merged_all["rms_error"].max()
            mean_error_total = merged_all["rms_error"].mean()

            # Making sure that min, max, mean errors are not > 100%
            if min_error_total > 100:
                min_error_total = 100

            if max_error_total > 100:
                max_error_total = 100

            if mean_error_total > 100:
                mean_error_total = 100

            # logging.infoing min, max, mean errors to the consol
            logging.info(
                f"# Device {dev} Cg{cap} min error: {min_error_total:.2f}, max error: {max_error_total:.2f}, mean error {mean_error_total:.2f}"
            )

            if max_error_total < PASS_THRESH:
                logging.info(f"# Device {dev} Cg{cap} has passed regression.")
            else:
                logging.error(f"# Device {dev} Cg{cap} has failed regression.")


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
