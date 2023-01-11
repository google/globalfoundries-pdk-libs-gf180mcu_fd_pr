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

from docopt import docopt
import pandas as pd
import numpy as np
import os
from jinja2 import Template
import concurrent.futures
import shutil
import multiprocessing as mp
import logging

import glob

import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

DEFAULT_TEMP = 25.0
PASS_THRESH = 2.0
MAX_VOLTAGE = 3.3


def find_diode(filepath):
    """
    Find diode in csv files
    """
    return os.path.exists(filepath)


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    os.system(f"Xyce -hspice-ext all {file_name} -l {file_name}.log 2> /dev/null")


def ext_iv_measured(
    dev_data_path: str, device: str, corners: str, dev_path: str
) -> pd.DataFrame:
    """ext_measured function  get measured data
    Args:
        dev_data_path (str): measured data path
        device (str): device name
        corners (str): corner name
        dev_path (str): device [path]

    Returns:
        df: output dataframe
    """
    # Read Data
    df = pd.read_excel(dev_data_path)

    dim_df = df[["L (um)", "W (um)"]].copy()
    dim_df.rename(
        columns={"L (um)": "length", "W (um)": "width"},
        inplace=True,
    )

    all_dfs = []

    loops = dim_df["length"].count()
    for corner in corners:

        for i in range(0, loops):
            width = dim_df["width"].iloc[int(i)]
            length = dim_df["length"].iloc[int(i)]

            if i % 4 == 0:
                temp = -40
            elif i % 4 == 1:
                temp = 25
            elif i % 4 == 2:
                temp = 125
            else:
                temp = 175

            leng = []
            wid = []
            tempr = []
            cor = []
            meas = []

            if i == 0:
                idf = df[["Vn1 (V)", f" |In1(A)| diode_{corner}"]].copy()
                idf.rename(
                    columns={
                        f" |In1(A)| diode_{corner}": "diode_measured",
                        "Vn1 (V)": "measured_volt",
                    },
                    inplace=True,
                )

            else:

                idf = df[["Vn1 (V)", f" |In1(A)| diode_{corner}.{i}"]].copy()
                idf.rename(
                    columns={
                        f" |In1(A)| diode_{corner}.{i}": "diode_measured",
                        "Vn1 (V)": "measured_volt",
                    },
                    inplace=True,
                )
            meas_csv = f"measured_A{width}_P{length}_t{temp}_{corner}.csv"

            os.makedirs(f"{dev_path}/measured_iv", exist_ok=True)
            idf.to_csv(f"{dev_path}/measured_iv/{meas_csv}")

            leng.append(length)
            wid.append(width)
            tempr.append(temp)
            cor.append(corner)
            meas.append(f"{dev_path}/measured_iv/{meas_csv}")

            sdf = {
                "length": leng,
                "width": wid,
                "temp": tempr,
                "corner": cor,
                "diode_measured": meas,
            }
            sdf = pd.DataFrame(sdf)
            all_dfs.append(sdf)

    df = pd.concat(all_dfs)
    df.dropna(axis=0, inplace=True)
    df["device"] = device
    df = df[["device", "length", "width", "temp", "corner", "diode_measured"]]

    return df


def run_sim(
    char: str,
    dirpath: str,
    device: str,
    length: float,
    width: float,
    corner: str,
    temp: float,
) -> dict:
    """Run simulation at specific information and corner
    Args:
        char (str): spice file name
        dirpath (str): device path
        device (str): device name
        length (float): length of device
        width (float): width of device
        corner (str): simulation corner
        temp (float): tempreture of device

    Returns:
        info(dict): results are stored in,
        and passed to the run_sims function to extract data"""
    netlist_tmp = f"./device_netlists/{char}.spice"

    info = {}
    info["device"] = device
    info["corner"] = corner
    info["temp"] = temp
    info["width"] = width
    info["length"] = length

    width_str = "{:.1f}".format(width)
    length_str = "{:.1f}".format(length)
    temp_str = "{:.1f}".format(temp)

    net_sp = f"netlist_A{width_str}_P{length_str}_t{temp_str}_{corner}.spice"
    res_csv = f"simulated_A{width_str}_P{length_str}_t{temp_str}_{corner}.csv"
    netlist_path = f"{dirpath}/{device}_netlists_{char}/{net_sp}"
    result_path = f"{dirpath}/simulated_{char}/{res_csv}"

    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        os.makedirs(f"{dirpath}/{device}_netlists_{char}", exist_ok=True)
        os.makedirs(f"{dirpath}/simulated_{char}", exist_ok=True)

        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device,
                    area=width_str,
                    pj=length_str,
                    Id_sim=char,
                    corner=corner,
                    temp=temp_str,
                )
            )

    # Running ngspice for each netlist
    try:
        call_simulator(netlist_path)
        # Find diode in csv
        if find_diode(result_path):
            diode_simu = result_path
        else:
            diode_simu = "None"
    except Exception:
        diode_simu = "None"

    info["diode_sim_unscaled"] = diode_simu

    return info


def run_sims(
    char: str, df: pd.DataFrame, dirpath: str, num_workers=mp.cpu_count()
) -> pd.DataFrame:
    """Run simulation at specific information and corner
    Args:
        char (str): sim file name
        df (pd.DataFrame): df has simulation info l,w,t
        dirpath (str): device path
        num_workers (_type_, optional): num of cores. Defaults to mp.cpu_count().

    Returns:
        pd.DataFrame: simulation df output
    """
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures_list = []
        for j, row in df.iterrows():
            futures_list.append(
                executor.submit(
                    run_sim,
                    char,
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
                logging.info("Test case generated an exception: %s" % (exc))

    sf = glob.glob(f"{dirpath}/simulated_{char}/*.csv")  # stored simulated data files
    for i in range(len(sf)):
        sdf = pd.read_csv(
            sf[i],
            header=None,
            delimiter=r"\s+",
        )
        sdf.drop(index=0, inplace=True)
        sdf.rename(
            columns={0: "diode_simulated"},
            inplace=True,
        )
        sdf.to_csv(sf[i], index=False)
        sdf = pd.read_csv(sf[i])
        sdf.to_csv(sf[i], index=True)

    df = pd.DataFrame(results)

    df = df[["device", "length", "width", "temp", "corner", "diode_sim_unscaled"]]
    df["diode_sim"] = df["diode_sim_unscaled"]

    return df


def main():
    """Main function applies all regression steps"""
    # ======= Checking Xyce  =======
    Xyce_v_ = os.popen("Xyce  -v 2> /dev/null").read()
    if Xyce_v_ == "":
        logging.error("Xyce is not found. Please make sure Xyce is installed.")
        exit(1)
    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    main_regr_dir = "diode_regr"

    # diode var.
    corners = ["typical", "ff", "ss"]

    devices = [
        "diode_dw2ps",
        "diode_pw2dw",
        "diode_nd2ps_03v3",
        "diode_nd2ps_06v0",
        "diode_nw2ps_03v3",
        "diode_nw2ps_06v0",
        "diode_pd2nw_03v3",
        "diode_pd2nw_06v0",
        "sc_diode",
    ]

    char = ["iv"]  # ,"cv"

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(f"{dev_path}", exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {dev}")

        for c in char:

            # cv section

            diode_data_files = glob.glob(f"./0_measured_data/{dev}_{c}.nl_out.xlsx")
            if len(diode_data_files) < 1:
                logging.error(f"# Can't find diode file for device: {dev}")
                diode_file = ""
            else:
                diode_file = diode_data_files[0]
            logging.info(f"# diode_{c} data points file : {diode_file}")

            avail_mess = f"# No {c}_datapoints available for"
            if diode_file == "":
                logging.info(f"{avail_mess} validation for device {dev}")
                continue
            f = ext_iv_measured

            if diode_file != "":
                meas_df = f(diode_file, dev, corners, dev_path)
            else:
                meas_df = []

            meas_len = len(pd.read_csv(glob.glob(f"{dev_path}/measured_{c}/*.csv")[1]))

            logging.info(
                f"# Device {dev} number of {c}_measured_datapoints : {len(meas_df) * meas_len}"
            )

            sim_df = run_sims(c, meas_df, dev_path, 3)
            sim_len = len(pd.read_csv(glob.glob(f"{dev_path}/simulated_{c}/*.csv")[1]))
            logging.info(
                f"# Device {dev} number of {c}_simulated datapoints : {len(sim_df) * sim_len}"
            )

            # compare section

            merged_df = meas_df.merge(
                sim_df, on=["device", "corner", "length", "width", "temp"], how="left"
            )
            merged_dfs = []
            for i in range(len(merged_df)):
                measured_data = pd.read_csv(merged_df["diode_measured"][i])
                simulated_data = pd.read_csv(merged_df["diode_sim"][i])
                simulated_data
                result_data = simulated_data.merge(measured_data, how="left")
                result_data["corner"] = (
                    merged_df["diode_measured"][i]
                    .split("/")[-1]
                    .split("_")[-1]
                    .split(".")[0]
                )
                result_data["device"] = merged_df["diode_measured"][i].split("/")[1]
                result_data["length"] = (
                    merged_df["diode_measured"][i]
                    .split("/")[-1]
                    .split("_")[1]
                    .split("A")[1]
                )
                result_data["width"] = (
                    merged_df["diode_measured"][i]
                    .split("/")[-1]
                    .split("_")[2]
                    .split("P")[1]
                )
                result_data["temp"] = (
                    merged_df["diode_measured"][i]
                    .split("/")[-1]
                    .split("_")[3]
                    .split("t")[1]
                )

                result_data["error"] = (
                    np.abs(
                        result_data["diode_simulated"] - result_data["diode_measured"]
                    )
                    * 100.0
                    / result_data["diode_measured"]
                )

                result_data = result_data[
                    [
                        "device",
                        "length",
                        "width",
                        "temp",
                        "corner",
                        "measured_volt",
                        "diode_measured",
                        "diode_simulated",
                        "error",
                    ]
                ]

                merged_dfs.append(result_data)

            merged_out = pd.concat(merged_dfs)

            merged_out.to_csv(f"{dev_path}/error_analysis_{c}.csv", index=False)

            if merged_out["error"].min() > 100:
                min_error = 100
            else:
                min_error = merged_out["error"].min()

            if merged_out["error"].max() > 100:
                max_error = 100
            else:
                max_error = merged_out["error"].max()

            if merged_out["error"].mean() > 100:
                mean_error = 100
            else:
                mean_error = merged_out["error"].mean()

            logging.info(
                f"# Device {dev} min error: {min_error:.2f}, max error: {max_error:.2f}, mean error {mean_error:.2f}"
            )

            if merged_out["error"].max() < PASS_THRESH:
                logging.info(f"# Device {dev} has passed regression.")
            else:
                logging.error(
                    f"# Device {dev} has failed regression. Needs more analysis."
                )


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
