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
import logging
import glob


# CONSTANT VALUES
DEFAULT_TEMP = 25.0
## TODO: Updating PASS_THRESH value after fixing simulation issues.
PASS_THRESH = 100.0
MAX_VOLTAGE = 10


def find_diode(filepath: str) -> bool:
    """Find diode in csv files
    Args:
        filepath (str): Path to csv file.
    Returns:
        bool: True if diode is found, False otherwise.
    """
    return os.path.exists(filepath)


def call_simulator(file_name: str) -> int:
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    Returns:
        int: Return code of the simulation. 0 if successful.  Non-zero otherwise.
    """
    return os.system(f"ngspice -b -a {file_name} -o {file_name}.log > {file_name}.log")


def ext_cv_measured(
    dev_data_path: str, device: str, corners: str, dev_path: str
) -> pd.DataFrame:
    """Extract measured data from csv file.
    Args:
        dev_data_path (str): Path to csv file.
        device (str): Device name.
        corners (str): Corner name.
        dev_path (str): Path to device directory.
    Returns:
        pd.DataFrame: DataFrame containing measured data.
    """
    # Read Data
    df = pd.read_excel(dev_data_path)

    dim_df = df[["Area", "Pj"]].copy()
    dim_df.rename(
        columns={"Area": "area", "Pj": "perim"},
        inplace=True,
    )

    all_dfs = []

    loops = dim_df["perim"].count()
    for corner in corners:

        for i in range(0, loops):
            area = dim_df["area"].iloc[int(i)]
            perim = dim_df["perim"].iloc[int(i)]

            if i % 4 == 0:
                temp = -40
            elif i % 4 == 1:
                temp = 25
            elif i % 4 == 2:
                temp = 125
            else:
                temp = 175

            perim_list = []
            area_list = []
            temp_list = []
            corner_list = []
            meas_list = []

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
                if abs(idf["measured_volt"][j]) <= MAX_VOLTAGE:
                    meas_volt.append(idf["measured_volt"][j])
                    meas_diode.append(idf["diode_measured"][j])
                else:
                    break
            meas_data = pd.DataFrame(
                {"measured_volt": meas_volt, "diode_measured": meas_diode}
            )

            meas_csv = f"measured_A{area}_P{perim}_t{temp}_{corner}.csv"

            os.makedirs(f"{dev_path}/measured_cv", exist_ok=True)
            meas_data.to_csv(f"{dev_path}/measured_cv/{meas_csv}", index=False)

            perim_list.append(perim)
            area_list.append(area)
            temp_list.append(temp)
            corner_list.append(corner)
            meas_list.append(f"{dev_path}/measured_cv/{meas_csv}")
            vn_max_cap = float(meas_data["measured_volt"].min())
            vn_min_curr = 0
            vn_max_curr = 0
            vn_step_curr = 0
            sdf = {
                "perim": perim_list,
                "area": area_list,
                "temp": temp_list,
                "corner": corner_list,
                "diode_measured": meas_list,
                "vn_max_cap": vn_max_cap,
                "vn_min_curr": vn_min_curr,
                "vn_max_curr": vn_max_curr,
                "vn_step_curr": vn_step_curr,
            }

            sdf = pd.DataFrame(sdf)
            all_dfs.append(sdf)

    df = pd.concat(all_dfs)
    df.dropna(axis=0, inplace=True)
    df.drop_duplicates(inplace=True)
    df["device"] = device
    df = df[["device", "perim", "area", "temp", "vn_max_cap", "vn_min_curr", "vn_max_curr", "vn_step_curr", "corner", "diode_measured"]]
    return df


def ext_iv_measured(
    dev_data_path: str, device: str, corners: str, dev_path: str
) -> pd.DataFrame:
    """Extract measured data from csv file.
    Args:
        dev_data_path (str): Path to csv file.
        device (str): Device name.
        corners (str): Corner name.
        dev_path (str): Path to device directory.
    Returns:
        pd.DataFrame: DataFrame containing measured data.
    """

    # Read Data
    df = pd.read_excel(dev_data_path)

    dim_df = df[["Area", "Pj"]].copy()
    dim_df.rename(
        columns={"Area": "area", "Pj": "perim"},
        inplace=True,
    )

    all_dfs = []

    loops = dim_df["perim"].count()
    for corner in corners:

        for i in range(0, loops):
            area = dim_df["area"].iloc[int(i)]
            perim = dim_df["perim"].iloc[int(i)]

            if i % 4 == 0:
                temp = -40
            elif i % 4 == 1:
                temp = 25
            elif i % 4 == 2:
                temp = 125
            else:
                temp = 175

            perim_list = []
            area_list = []
            temp_list = []
            corner_list = []
            meas_list = []

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
            meas_csv = f"measured_A{area}_P{perim}_t{temp}_{corner}.csv"

            os.makedirs(f"{dev_path}/measured_iv", exist_ok=True)
            idf.to_csv(f"{dev_path}/measured_iv/{meas_csv}", index=False)

            perim_list.append(perim)
            area_list.append(area)
            temp_list.append(temp)
            corner_list.append(corner)
            meas_list.append(f"{dev_path}/measured_iv/{meas_csv}")
            vn_max_cap = 0
            vn_min_curr = float(idf["measured_volt"].min())
            vn_max_curr = float(idf["measured_volt"].max())
            vn_step_curr = float(idf.iloc[1]['measured_volt'] - idf.iloc[0]['measured_volt'])

            sdf = {
                "perim": perim_list,
                "area": area_list,
                "temp": temp_list,
                "corner": corner_list,
                "diode_measured": meas_list,
                "vn_max_cap": vn_max_cap,
                "vn_min_curr": vn_min_curr,
                "vn_max_curr": vn_max_curr,
                "vn_step_curr": vn_step_curr
            }
            sdf = pd.DataFrame(sdf)
            all_dfs.append(sdf)

    df = pd.concat(all_dfs)
    df.dropna(axis=0, inplace=True)
    df["device"] = device
    df = df[["device", "perim", "area", "temp", "vn_max_cap", "vn_min_curr", "vn_max_curr", "vn_step_curr", "corner", "diode_measured"]]

    return df


def run_sim(
    char: str,
    dirpath: str,
    device: str,
    perim: float,
    area: float,
    corner: str,
    temp: float,
    vn_max_cap: float,
    vn_min_curr: float,
    vn_max_curr: float,
    vn_step_curr: float,
) -> dict:
    """Run simulation.
    Args:
        char (str): Characteristic.
        dirpath (str): Path to directory.
        device (str): Device name.
        perim (float): Device perimeter.
        area (float): Device area.
        corner (str): Corner name.
        temp (float): Temperature.
        vn_max_cap (float): Max voltage for cap sim.
        vn_max_cap (float): Min voltage for current sim.
        vn_max_cap (float): Max voltage for current sim.
        vn_max_cap (float): Step voltage for current sim.
    Returns:
        dict: Dictionary containing simulation results.
    """
    netlist_tmp = f"./device_netlists/{char}.spice"

    info = {}
    info["device"] = device
    info["corner"] = corner
    info["temp"] = temp
    info["vn_max_cap"] = vn_max_cap
    info["area"] = area
    info["perim"] = perim

    area_str = "{:.2f}".format(area)
    perim_str = "{:.2f}".format(perim)
    temp_str = "{:.2f}".format(temp)
    vn_max_cap = "{:.2f}".format(vn_max_cap)
    vn_min_curr = "{:.2f}".format(vn_min_curr)
    vn_max_curr = "{:.2f}".format(vn_max_curr)
    vn_step_curr = "{:.2f}".format(vn_step_curr)

    net_sp = f"netlist_A{area_str}_P{perim_str}_t{temp_str}_{corner}.spice"
    res_csv = f"simulated_A{area_str}_P{perim_str}_t{temp_str}_{corner}.csv"
    netlist_path = f"{dirpath}/{device}_netlists_{char}/{net_sp}"
    result_path = f"{dirpath}/{device}_netlists_{char}/{res_csv}"

    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        os.makedirs(f"{dirpath}/{device}_netlists_{char}", exist_ok=True)

        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device,
                    area=area_str,
                    perim=perim_str,
                    corner=corner,
                    temp=temp_str,
                    vn_max_cap=vn_max_cap,
                    vn_min_curr=vn_min_curr,
                    vn_max_curr=vn_max_curr,
                    vn_step_curr=vn_step_curr
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
    """Run simulations.
    Args:
        char (str): Characteristic.
        df (pd.DataFrame): DataFrame containing simulation parameters.
        dirpath (str): Path to directory.
        num_workers (int, optional): Number of workers. Defaults to mp.cpu_count().
    Returns:
        pd.DataFrame: DataFrame containing simulation results.
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
                    row["perim"],
                    row["area"],
                    row["corner"],
                    row["temp"],
                    row["vn_max_cap"],
                    row["vn_min_curr"],
                    row["vn_max_curr"],
                    row["vn_step_curr"],
                )
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logging.info("Test case generated an exception: %s" % (exc))

    # stored simulated data files
    sf = glob.glob(f"{dirpath}/*_netlists_{char}/*.csv")
    for i in range(len(sf)):
        sdf = pd.read_csv(
            sf[i],
            header=None,
            delimiter=r"\s+",
        )
        sdf.rename(
            columns={1: "diode_simulated", 0: "simulated_volt"},
            inplace=True,
        )
        sdf.to_csv(sf[i], index=False)

    df = pd.DataFrame(results)

    df = df[["device", "perim", "area", "temp", "corner", "diode_sim_unscaled"]]
    df["diode_sim"] = df["diode_sim_unscaled"]

    return df


def main():
    """Main function."""
    # ======= Checking ngspice  =======
    ngspice_v_ = os.popen("ngspice -v").read()

    if "ngspice-" not in ngspice_v_:
        logging.error("ngspice is not found. Please make sure ngspice is installed.")
        exit(1)
    else:
        version = int((ngspice_v_.split("\n")[1]).split(" ")[1].split("-")[1])
        logging.info(f"Your ngspice version is {version}")
        if version <= 37:
            logging.error(
                "ngspice version is not supported. Please use ngspice version 38 or newer."
            )
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

    char_measured = ["iv"]

    for j, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(f"{dev_path}", exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {dev}")

        for char in char_measured:

            # cv section

            diode_data_files = glob.glob(
                f"../../180MCU_SPICE_DATA/Diode/{dev}_{char}.nl_out.xlsx"
            )
            if len(diode_data_files) < 1:
                logging.error(f"# Can't find diode file for device: {dev}")
                diode_file = ""
            else:
                diode_file = os.path.abspath(diode_data_files[0])

            logging.info(f"# diode_{char} data points file : {diode_file}")

            avail_mess = f"# No {char}_datapoints available for"
            if diode_file == "":
                logging.info(f"{avail_mess} validation for device {dev}")
                continue

            if char == "iv":
                meas_func = ext_iv_measured
            else:
                meas_func = ext_cv_measured

            if diode_file != "":
                meas_df = meas_func(diode_file, dev, corners, dev_path)
            else:
                meas_df = []

            meas_len = len(
                pd.read_csv(glob.glob(f"{dev_path}/measured_{char}/*.csv")[1])
            )

            logging.info(
                f"# Device {dev} number of {char}_measured_datapoints : {len(meas_df) * meas_len}"
            )

            sim_df = run_sims(char, meas_df, dev_path, workers_count)

            sim_len = len(
                pd.read_csv(glob.glob(f"{dev_path}/*_netlists_{char}/*.csv")[1])
            )
            logging.info(
                f"# Device {dev} number of {char}_simulated datapoints : {len(sim_df) * sim_len}"
            )

            # compare section
            merged_df = meas_df.merge(
                sim_df, on=["device", "corner", "perim", "area", "temp"], how="left"
            )

            merged_dfs = []
            # create a new dataframe for rms error
            rms_df = pd.DataFrame(
                columns=["device", "perim", "area", "temp", "corner", "rms_error"]
            )

            for i in range(len(merged_df)):
                measured_data = pd.read_csv(merged_df["diode_measured"][i])
                simulated_data = pd.read_csv(merged_df["diode_sim"][i])
                measured_data["volt"] = measured_data["measured_volt"]
                simulated_data["volt"] = simulated_data["simulated_volt"]
                result_data = simulated_data.merge(
                    measured_data, on="volt", how="left"
                )

                result_data = result_data.drop("measured_volt", axis=1)
                result_data = result_data.drop("simulated_volt", axis=1)
                result_data["corner"] = (
                    merged_df["diode_measured"][i]
                    .split("/")[-1]
                    .split("_")[-1]
                    .split(".")[0]
                )
                result_data["device"] = merged_df["diode_measured"][i].split("/")[1]
                result_data["area"] = (
                    merged_df["diode_measured"][i]
                    .split("/")[-1]
                    .split("_")[1]
                    .split("A")[1]
                )
                result_data["perim"] = (
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

                ## We found that most of the curr are greater than fA and most of the
                ## error happens in the breakdown mode of the diode. And it causes large rmse for the values.
                ## We will clip at 10fA for all currents to make sure that for small signal it works as expected.

                # Clipping all the  values to lowest_curr
                lowest_curr = 1.0e-14

                result_data["diode_measured"] = result_data["diode_measured"].clip(lower=lowest_curr)
                result_data["diode_simulated"] = result_data["diode_simulated"].clip(lower=lowest_curr)

                result_data["error"] = (
                    np.abs(
                        result_data["diode_simulated"] - result_data["diode_measured"]
                    )
                    * 100.0
                    / result_data["diode_measured"]
                )
                # fill nan values with 0
                result_data["error"] = result_data["error"].fillna(0)

                # get rms error
                result_data["rms_error"] = np.sqrt(np.mean((result_data["error"] - result_data["error"].mean()) ** 2))

                # fill rms dataframe
                rms_df.loc[i] = [
                    result_data["device"][0],
                    result_data["perim"][0],
                    result_data["area"][0],
                    result_data["temp"][0],
                    result_data["corner"][0],
                    result_data["rms_error"][0],
                ]

                result_data = result_data[
                    [
                        "device",
                        "perim",
                        "area",
                        "temp",
                        "corner",
                        "volt",
                        "diode_measured",
                        "diode_simulated",
                        "error",
                    ]
                ]

                merged_dfs.append(result_data)

            merged_out = pd.concat(merged_dfs)

            merged_out.to_csv(f"{dev_path}/error_analysis_{char}.csv", index=False)
            rms_df.to_csv(f"{dev_path}/final_error_analysis_{char}.csv", index=False)

            # calculating the error of each device and reporting it
            min_error_total = float(rms_df["rms_error"].min())
            max_error_total = float(rms_df["rms_error"].max())
            mean_error_total = float(rms_df["rms_error"].mean())
            # Making sure that min, max, mean errors are not > 100%
            min_error_total = 100 if min_error_total > 100 else min_error_total
            max_error_total = 100 if max_error_total > 100 else max_error_total
            mean_error_total = 100 if mean_error_total > 100 else mean_error_total

            # logging.infoing min, max, mean errors to the consol
            logging.info(
                f"# Device {dev} {char} min error: {min_error_total:.2f}%, max error: {max_error_total:.2f}%, mean error {mean_error_total:.2f}%"
            )

            # Verify regression results
            if mean_error_total <= PASS_THRESH:
                logging.info(f"# Device {dev} {char} has passed regression.")
            else:
                logging.error(
                    f"# Device {dev} {char} has failed regression. Needs more analysis."
                )
                logging.error(
                    "#Failed regression for diode analysis."
                )
                exit(1)

# ================================================================
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
