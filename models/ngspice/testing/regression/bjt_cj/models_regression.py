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

PASS_THRESH = 5.0  # threshold value for passing devices
NO_ROWS_NPN = 54  # no.of combinations extracted from npn sheet
NO_ROWS_PNP = 24  # no.of combinations extracted from pnp sheet
NO_ROWS_NPN_W = 36  # no.of combinations extracted from npn sheet without csj


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


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name(str): Netlist file name.
    """
    return os.system(f"ngspice -b -a {file_name} -o {file_name}.log > {file_name}.log")


def ext_measured(
    cj_file: str, dev: str, devices: list, dev_path: str, no_rows=int
) -> pd.DataFrame:
    """Extracting the measured data of npn devices from excel sheet

    Args:
         cj_file(str): path to the data sheet
         dev(str): device name whether npn or pnp
         devices(list): list for undertest devices
         dev_path(str): A path where extracted data is stored
         no_rows(int): no.of combinations extracted from npn, pnp sheet

    Returns:
         df_measured(pd.DataFrame): A data frame contains all extracted data

    """

    # Reading excel sheet and creating data frame
    df = pd.read_excel(cj_file)

    # temp_range is threshold for switching between 25, -40, 125
    temp_range = int(no_rows / 3)
    # initiating empty list for appendindurationg dataframes
    all_dfs = list()

    # Extracting measured values for each Device
    for i in range(no_rows):

        # building up temperature
        if i in range(0, temp_range):
            temp = 25.0
        elif i in range(temp_range, 2 * temp_range):
            temp = -40.0
        else:
            temp = 175.0

        # extracted columns from sheet
        temp_value = list()
        dev_names = list()
        cj_measured = list()
        cap_names = list()

        # reading third column for getting device name, cap_name
        data = df["Unnamed: 2"][i]  # data is a string now
        cap_name = data[4:7]
        # as CSJ make NAN
        if cap_name == "CSJ":
            continue
        end_location = data.find("(")
        read_dev_name = data[8:end_location]
        space = read_dev_name.find(" ")
        read_dev_name = read_dev_name[0:space]

        # renaming the device like the standard
        # for npn devices:
        if dev == "npn":
            if read_dev_name == "10x10":
                dev_name = devices[0]
            elif read_dev_name == "5x5":
                dev_name = devices[1]
            elif read_dev_name == "0p54x16":
                dev_name = devices[2]
            elif read_dev_name == "0p54x8":
                dev_name = devices[3]
            elif read_dev_name == "0p54x4":
                dev_name = devices[4]
            elif read_dev_name == "0p54x2":
                dev_name = devices[5]

        # for pnp devices:
        elif dev == "pnp":
            if read_dev_name == "0p42x10":
                dev_name = devices[0]
            elif read_dev_name == "0p42x5":
                dev_name = devices[1]
            elif read_dev_name == "10x10":
                dev_name = devices[2]
            elif read_dev_name == "5x5":
                dev_name = devices[3]

        # extracting C-V measured data
        # Special case for 1st measured values
        if i == 0:
            cj_values = df[["Vj", "bjt_typical", "bjt_ff", "bjt_ss"]].copy()

            cj_values.rename(
                columns={
                    "Vj": "volt",
                    "bjt_typical": "measured_bjt_typical",
                    "bjt_ff": "measured_bjt_ff",
                    "bjt_ss": "measured_bjt_ss",
                },
                inplace=True,
            )

        else:
            cj_values = df[
                ["Vj", f"bjt_typical.{i}", f"bjt_ff.{i}", f"bjt_ss.{i}"]
            ].copy()

            cj_values.rename(
                columns={
                    "Vj": "volt",
                    f"bjt_typical.{i}": "measured_bjt_typical",
                    f"bjt_ff.{i}": "measured_bjt_ff",
                    f"bjt_ss.{i}": "measured_bjt_ss",
                },
                inplace=True,
            )

        os.makedirs(f"{dev_path}/cj_measured", exist_ok=True)
        cj_values.dropna(axis=0, inplace=True)
        cj_values.to_csv(
            f"{dev_path}/cj_measured/measured_{dev_name}_t{temp}_{cap_name}.csv",
            index=False,
        )

        dev_names.append(dev_name)
        cap_names.append(cap_name)
        temp_value.append(temp)
        cj_measured.append(
            f"{dev_path}/cj_measured/measured_{dev_name}_t{temp}_{cap_name}.csv"
        )

        sdf = {
            "device": dev_names,
            "temp": temp_value,
            "cap": cap_names,
            "cj_measured": cj_measured,
        }
        sdf = pd.DataFrame(sdf)
        all_dfs.append(sdf)

    df = pd.concat(all_dfs)
    df.dropna(axis=0, inplace=True)
    return df


def run_sim(dirpath: str, cap: str, device: str, temp: float) -> dict:
    """Run simulation at specific information and corner
    Args:
        dirpath(str): path to the file where we write data
        cap(str): under-test cap to select proper netlist
        device(str): the device instance will be simulated
        temp(float): a specific temp for simulation

    Returns:
        info(dict): results are stored in,
        and passed to the run_sims function to extract data
    """

    corners = ["typical", "ff", "ss"]
    for corner in corners:
        info = dict()
        info["device"] = device
        info["temp"] = temp
        info["cap"] = cap

        dev = device.split("_")[0]

        netlist_tmp = f"device_netlists/{dev}_{cap}.spice"
        temp_str = "{:.1f}".format(temp)
        netlist_path = f"{dirpath}/{dev}_netlists/netlist_{device}_t{temp_str}_{cap}_{corner}.spice"

        result_path = f"{dirpath}/cj_simulated/simulated_{device}_t{temp_str}_{cap}.csv"
        result_path_corner = (
            f"{dirpath}/cj_simulated/simulated_{device}_t{temp_str}_{cap}_{corner}.csv"
        )
        # initiating the directory in which results will be stored
        os.makedirs(f"{dirpath}/cj_simulated", exist_ok=True)

        with open(netlist_tmp) as f:
            tmpl = Template(f.read())
            os.makedirs(f"{dirpath}/{dev}_netlists", exist_ok=True)

            with open(netlist_path, "w") as netlist:
                netlist.write(
                    tmpl.render(
                        dirpath=dirpath,
                        device=device,
                        temp=temp_str,
                        cap=cap,
                        corner=corner,
                    )
                )
            with open(netlist_path, "r") as netlist:
                netlist_str = netlist.read()
            netlist_str.replace(".endend", ".end")
            # logging.info(netlist_str)
            # exit()
            with open(netlist_path, "w") as netlist:
                netlist.write(netlist_str)

        # Running ngspice for each netlist
        try:
            call_simulator(netlist_path)

            # check if results stored in csv file or not!
            if os.path.exists(result_path_corner):
                bjt_simu_cj = result_path
            else:
                bjt_simu_cj = "None"

        except Exception:
            bjt_simu_cj = "None"

    info["cj_simulated"] = bjt_simu_cj

    return info


def run_sims(df: pd.DataFrame, dirpath: str, num_workers=mp.cpu_count()):
    """passing netlists to run_sim function
        and storing the results csv files into dataframes

    Args:ext_npn_measured
        df(pd.DataFrame): dataframe passed from the ext_measured function
        dirpath(str): the path to the file where we write data
        num_workers=mp.cpu_count() (int): num of cpu used

    Returns:
        df(pd.DataFrame): dataframe contains simulated results
    """

    results = list()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures_list = list()
        for j, row in df.iterrows():
            futures_list.append(
                executor.submit(
                    run_sim, dirpath, row["cap"], row["device"], row["temp"]
                )
            )
        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logging.info(f"Test case generated an exception: {exc}")

    sf = glob.glob(f"{dirpath}/cj_simulated/*.csv")
    sf.sort()

    # sweeping on all generated cvs files
    for i in range(0, len(sf), 3):
        sdf = pd.read_csv(sf[i], header=None, delimiter=r"\s+")
        sweep = len(pd.read_csv(glob.glob(f"{dirpath}/cj_measured/*.csv")[1]))
        new_array = np.empty((sweep, 4))
        new_array[:, 0] = sdf.iloc[:sweep, 0]
        new_array[:, 1] = sdf.iloc[:sweep, 1]

        sdf = pd.read_csv(sf[i + 1], header=None, delimiter=r"\s+")
        new_array[:, 2] = sdf.iloc[:sweep, 1]

        sdf = pd.read_csv(sf[i + 2], header=None, delimiter=r"\s+")
        new_array[:, 3] = sdf.iloc[:sweep, 1]

        # Writing final simulated data 1
        final_sim_res = sf[i].replace("_ff", "")

        sdf = pd.DataFrame(new_array)
        sdf.to_csv(final_sim_res, index=False)
        sdf.rename(
            columns={
                0: "volt",
                1: "simulated_bjt_ff",
                2: "simulated_bjt_ss",
                3: "simulated_bjt_typical",
            },
            inplace=True,
        )
        sdf.iloc[:, 0:].to_csv(final_sim_res, index=False)
    df = pd.DataFrame(results)

    return df


def error_cal(merged_df: pd.DataFrame, dev_path: str) -> None:
    """error function calculates the error between measured, simulated data

    Args:
        merged_df(pd.DataFrame): Dataframe contains devices and csv files
          which represent measured, simulated data
        dev_path(str): The path in which we write data
    """

    # adding error columns to the merged dataframe
    merged_dfs = list()
    # create a new dataframe for rms error
    rms_df = pd.DataFrame(columns=["device", "temp", "cap", "rms_error"])

    merged_df.drop_duplicates()
    for i in range(len(merged_df)):

        measured_data = pd.read_csv(merged_df["cj_measured"][i])
        simulated_data = pd.read_csv(
            merged_df["cj_measured"][i].replace("measured", "simulated")
        )

        result_data = pd.merge(measured_data, simulated_data, on="volt", how="left")

        result_data["cap"] = merged_df["cap"][i]
        result_data["device"] = (
            merged_df["cj_measured"][i].split("/")[-1].split("d_")[1].split("_t")[0]
        )
        result_data["temp"] = (
            merged_df["cj_measured"][i]
            .split("/")[-1]
            .split("_")[3]
            .split("t")[1]
            .split(".")[0]
        )
        result_data["error_bjt_typical"] = (
            np.abs(
                result_data["simulated_bjt_typical"]
                - result_data["measured_bjt_typical"]
            )
            * 100.0
            / result_data["measured_bjt_typical"]
        )

        result_data["error_bjt_ff"] = (
            np.abs(result_data["simulated_bjt_ff"] - result_data["measured_bjt_ff"])
            * 100.0
            / result_data["measured_bjt_ff"]
        )

        result_data["error_bjt_ss"] = (
            np.abs(result_data["simulated_bjt_ss"] - result_data["measured_bjt_ss"])
            * 100.0
            / result_data["measured_bjt_ss"]
        )
        result_data.fillna(0, inplace=True)
        result_data["error"] = (
            np.abs(
                result_data["error_bjt_ss"]
                + result_data["error_bjt_ff"]
                + result_data["error_bjt_typical"]
            )
            / 3
        )
        # get rms error
        result_data["rms_error"] = np.sqrt(np.mean(result_data["error"] ** 2))
        # fill rms dataframe
        rms_df.loc[i] = [
            result_data["device"][0],
            result_data["temp"][0],
            result_data["cap"][0],
            result_data["rms_error"][0],
        ]
        merged_dfs.append(result_data)
        merged_out = pd.concat(merged_dfs)
        merged_out.to_csv(f"{dev_path}/error_analysis.csv", index=False)
        rms_df.to_csv(f"{dev_path}/final_error_analysis.csv", index=False)
    return None


def main():
    """
    Main function applies all regression steps
    """

    ## Check ngspice version
    check_ngspice_version()

    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    main_regr_dir = "run_bjt_cj_regr"

    devices = ["npn", "pnp"]
    npn_devices = [
        "npn_10p00x10p00",
        "npn_05p00x05p00",
        "npn_00p54x16p00",
        "npn_00p54x08p00",
        "npn_00p54x04p00",
        "npn_00p54x02p00",
    ]

    pnp_devices = [
        "pnp_10p00x00p42",
        "pnp_05p00x00p42",
        "pnp_10p00x10p00",
        "pnp_05p00x05p00",
    ]

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(f"{dev_path}", exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {dev}")

        cj_data_files = glob.glob(
            f"../../180MCU_SPICE_DATA/BJT/bjt_cv_{dev}.nl_out.xlsx"
        )
        if len(cj_data_files) < 1:
            logging.info(f"# Can't find data file for device: {dev}")
            cj_file = ""
        else:
            cj_file = os.path.abspath(cj_data_files[0])
        logging.info(f"# bjt_cj data points file : {cj_file}")

        if cj_file == "":
            logging.info(f"# No datapoints available for validation for device {dev}")
            continue

        if dev == "npn":
            list_dev = npn_devices
            no_rows = NO_ROWS_NPN
        elif dev == "pnp":
            list_dev = pnp_devices
            no_rows = NO_ROWS_PNP

        if cj_file != "":
            meas_df = ext_measured(cj_file, dev, list_dev, dev_path, no_rows)
        else:
            meas_df = list()

        meas_len = len(pd.read_csv(glob.glob(f"{dev_path}/cj_measured/*.csv")[1]))
        logging.info(
            f"# Device {dev} number of measured_datapoints : {len(meas_df) * meas_len}"
        )

        # assuming number of used cores is 3
        # calling run_sims function for simulating devices
        sim_df = run_sims(meas_df, dev_path, workers_count)

        # Merging measured dataframe with the simulated one
        merged_df = meas_df.merge(sim_df, on=["device", "temp", "cap"], how="left")

        # passing dataframe to the error_calculation function
        # calling error function for creating statistical csv file
        error_cal(merged_df, dev_path)

        merged_all = pd.read_csv(f"{dev_path}/final_error_analysis.csv")
        # number of rows in the final excel sheet
        num_rows = merged_all["device"].count()

        # calculating the error of each device and reporting it
        for i in range(NO_ROWS_NPN_W):
            min_error_total = float()
            max_error_total = float()
            error_total = float()
            number_of_existance = int()

            # number of rows in the final excel sheet
            num_rows = merged_all["device"].count()

        # calculating the error of each device and reporting it
        for dev in list_dev:
            min_error_total = float()
            max_error_total = float()
            error_total = float()
            number_of_existance = int()

            # number of rows in the final excel sheet
            num_rows = merged_all["device"].count()

            for n in range(num_rows):
                if dev == merged_all["device"].iloc[n]:
                    number_of_existance += 1
                    error_total += merged_all["rms_error"].iloc[n]
                    if merged_all["rms_error"].iloc[n] > max_error_total:
                        max_error_total = merged_all["rms_error"].iloc[n]
                    elif merged_all["rms_error"].iloc[n] < min_error_total:
                        min_error_total = merged_all["rms_error"].iloc[n]
            mean_error_total = error_total / number_of_existance
            # Making sure that min, max, mean errors are not > 100%
            if min_error_total > 100:
                min_error_total = 100

            if max_error_total > 100:
                max_error_total = 100

            if mean_error_total > 100:
                mean_error_total = 100

            # logging.infoing min, max, mean errors to the consol
            logging.info(
                f"# Device {dev} min error: {min_error_total:.2f}, max error: {max_error_total:.2f}, mean error {mean_error_total:.2f}"
            )

            # Verify regression results
            if max_error_total < PASS_THRESH:
                logging.info(f"# Device {dev} has passed regression.")
            else:
                logging.error(
                    f"# Device {dev} has failed regression. Needs more analysis."
                )
                logging.error(
                    "#Failed regression for BJT-cj analysis."
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
