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
    return os.system(
        f"ngspice -b -a {file_name} -o {file_name}.log > {file_name}.log"
        )


def ext_cv_measured(dev_data_path, device, corners, dev_path):
    # Read Data
    df = pd.read_excel(dev_data_path)

    dim_df = df[["L (um)", "W (um)"]].copy()
    dim_df.rename(
        columns={"L (um)": "length", "W (um)": "width"}, inplace=True,
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
                idf = df[["Vj", f"diode_{corner}"]].copy()
                idf.rename(
                    columns={
                        f"diode_{corner}": "diode_measured",
                        "Vj": "measured_volt",
                    },
                    inplace=True,
                )

            else:

                idf = df[["Vj", f"diode_{corner}.{i}"]].copy()
                idf.rename(
                    columns={
                        f"diode_{corner}.{i}": "diode_measured",
                        "Vj": "measured_volt",
                    },
                    inplace=True,
                )

            meas_volt = []
            meas_diode = []
            for j in range(idf["measured_volt"].count()):
                if abs(idf["measured_volt"][j]) < MAX_VOLTAGE:
                    meas_volt.append(idf["measured_volt"][j])
                    meas_diode.append(idf["diode_measured"][j])
                else:
                    break
            meas_data = pd.DataFrame(
                {"measured_volt": meas_volt, "diode_measured": meas_diode}
            )

            meas_csv = f"measured_A{width}_P{length}_t{temp}_{corner}.csv"

            os.makedirs(f"{dev_path}/measured_cv", exist_ok=True)
            meas_data.to_csv(
                f"{dev_path}/measured_cv/{meas_csv}"
                )

            leng.append(length)
            wid.append(width)
            tempr.append(temp)
            cor.append(corner)
            meas.append(
                f"{dev_path}/measured_cv/{meas_csv}"
            )

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


def ext_iv_measured(dev_data_path, device, corners, dev_path):
    # Read Data
    df = pd.read_excel(dev_data_path)

    dim_df = df[["L (um)", "W (um)"]].copy()
    dim_df.rename(
        columns={"L (um)": "length", "W (um)": "width"}, inplace=True,
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
            idf.to_csv(
                f"{dev_path}/measured_iv/{meas_csv}"
            )

            leng.append(length)
            wid.append(width)
            tempr.append(temp)
            cor.append(corner)
            meas.append(
                f"{dev_path}/measured_iv/{meas_csv}"
            )

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


def run_sim(char, dirpath, device, length, width, corner, temp):
    """ Run simulation at specific information and corner """
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


def run_sims(char, df, dirpath, num_workers=mp.cpu_count()):

    results = []
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_workers) as executor:
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
                print("Test case generated an exception: %s" % (exc))

    sf = glob.glob(
        f"{dirpath}/simulated_{char}/*.csv")  # stored simulated data files
    for i in range(len(sf)):
        sdf = pd.read_csv(sf[i], header=None, delimiter=r"\s+",)
        sdf.rename(
            columns={1: "diode_simulated", 0: "simulated_volt"}, inplace=True,
        )
        sdf.to_csv(sf[i])

    df = pd.DataFrame(results)

    df = df[
        ["device", "length", "width", "temp", "corner", "diode_sim_unscaled"]
        ]
    df["diode_sim"] = df["diode_sim_unscaled"]

    return df


def main():

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

    char = ["cv", "iv"]

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(f"{dev_path}", exist_ok=False)

        print("######" * 10)
        print(f"# Checking Device {dev}")

        print("\n")

        for c in char:

            # cv section

            diode_data_files = glob.glob(
                f"./0_measured_data/{dev}_{c}.nl_out.xlsx"
                )
            if len(diode_data_files) < 1:
                print("# Can't find diode file for device: {}".format(dev))
                diode_file = ""
            else:
                diode_file = diode_data_files[0]
            print(f"# diode_{c} data points file : ", diode_file)

            avail_mess = "# No {c}_datapoints available for"
            if diode_file == "":
                print(
                    f"{avail_mess} validation for device {dev}"
                    )
                continue

            if "c" in c:
                f = ext_cv_measured
            elif "i" in c:
                f = ext_iv_measured

            if diode_file != "":
                meas_df = f(diode_file, dev, corners, dev_path)
            else:
                meas_df = []

            meas_len = len(
                pd.read_csv(glob.glob(f"{dev_path}/measured_{c}/*.csv")[1])
                )

            print(
                f"# Device {dev} number of {c}_measured_datapoints : ",
                len(meas_df) * meas_len,
            )

            sim_df = run_sims(c, meas_df, dev_path, 3)
            sim_len = len(
                pd.read_csv(glob.glob(f"{dev_path}/simulated_{c}/*.csv")[1])
                )
            print(
                f"# Device {dev} number of {c}_simulated datapoints : ",
                len(sim_df) * sim_len,
            )

            # compare section

            merged_df = meas_df.merge(
                sim_df, on=["device", "corner", "length", "width", "temp"],
                how="left"
            )

            merged_dfs = []
            for i in range(len(merged_df)):
                measured_data = pd.read_csv(merged_df["diode_measured"][i])
                simulated_data = pd.read_csv(merged_df["diode_sim"][i])
                result_data = simulated_data.merge(measured_data, how="left")
                result_data["corner"] = (
                    merged_df["diode_measured"][i]
                    .split("/")[-1]
                    .split("_")[-1]
                    .split(".")[0]
                )
                result_data["device"] = \
                    merged_df["diode_measured"][i].split("/")[1]
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
                        result_data["diode_simulated"]
                        - result_data["diode_measured"]
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

            merged_out.to_csv(
                f"{dev_path}/error_analysis_{c}.csv", index=False
                )

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

            print(
                "# Device {} min error: {:.2f}".format(
                    dev,
                    min_error
                ),
                " , max error: {:.2f}, mean error {:.2f}".format(

                    max_error,
                    mean_error
                )
            )

            if merged_out["error"].max() < PASS_THRESH:
                print("# Device {} has passed regression.".format(dev))
            else:
                print(
                    "# Device {} has failed regression. Needs more analysis."
                    .format(dev)
                )

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
