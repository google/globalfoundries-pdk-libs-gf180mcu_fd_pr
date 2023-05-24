# Copyright 2023 GlobalFoundries PDK Authors
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

  -h, --help                     Show help text.
  -v, --version                  Show version.
  --num_cores=<num>              Number of cores to be used by simulator
"""

from docopt import docopt
import pandas as pd
import numpy as np
from subprocess import check_call, Popen, PIPE
from jinja2 import Template
import concurrent.futures
import shutil
import glob
import os
import logging


# CONSTANT VALUES
PASS_THRESH = 5.0
# === RES-R ===
MAX_VAL_DETECT = 1  # Max value to detect bad errors above it
QUANTILE_RATIO = 0.98


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


def simulate_device(netlist_path: str):
    """
    Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist cir for run.
    Returns:
        int: Return code of the simulation. 0 if success.  Non-zero if failed.
    """
    return os.system(f"ngspice -b {netlist_path} -o {netlist_path}.log > {netlist_path}.log 2>&1")


def find_res(filename: str) -> float:
    """
    Find res in log
    """
    cmd = 'grep "res = " {} | head -n 1'.format(filename)
    process = Popen(cmd, shell=True, stdout=PIPE)
    return float(process.communicate()[0][:-1].decode("utf-8").split(" ")[2])


def run_sim(dirpath: str, device: str, width: str, length: float,
            corner: float, temp: float, voltage: str) -> dict:
    """
    Function to run simulation for all data points per each variation.

    Parameters
    ----------
    dirpath : str or Path
        Path to the run results directory
    device : str
        Device used in regression test
    meas_out_result : str
        Measurement selected to be test for the current regression.
    width: float
        Width value for the current run
    length: float
        length value for the current run
    temp: float
        temp value for the current run
    voltage: float
        voltage value for the current run
    Returns
    -------
    result_df: dict
        Dataframe contains results for the current run
    """

    # Select desired nelist templete to be used in the current run
    netlist_tmp = os.path.join("device_netlists", "res_r.spice")

    # Preparing output directory at which results will be added
    dev_netlists_path = os.path.join(dirpath, f"{device}_netlists")
    os.makedirs(dev_netlists_path, exist_ok=True)

    sp_file_name = f"netlist_w{width}_l{length}_t{temp}_{corner}_v{voltage}.spice"
    netlist_path = os.path.join(dev_netlists_path, sp_file_name)

    result_df = {}
    result_df["device"] = device
    result_df["width"] = width
    result_df["length"] = length
    result_df["temp"] = temp
    result_df["corner"] = corner
    result_df["voltage"] = voltage

    # Differientiate between 2 or 3 terminal res
    if "rm" in device or "tm" in device:
        terminals = "GND"
    else:
        terminals = "GND GND"

    # Generating netlist templates for all variations
    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device,
                    terminals=terminals,
                    width=width,
                    length=length,
                    temp=temp,
                    corner=corner,
                    voltage=voltage,
                )
            )

    # Running ngspice for each netlist
    logging.info(f"Running simulation for {device}-R at w={width}, l={length}, temp={temp}, corner={corner}, voltage={voltage}")

    # calling simulator to run netlist and write its results
    try:
        simulate_device(netlist_path)
        # Get res value from run log
        try:
            res_val = find_res(f"{netlist_path}.log")

        except Exception:
            res_val = np.nan
            logging.error(
                f"Running simulation at w={width}, l={length}, temp={temp}, corner={corner} got an exception"
            )
            logging.error(f"Regression couldn't get the output from {netlist_path}.log")
    except Exception:
        res_val = np.nan
        logging.error(
            f"Running simulation at w={width}, l={length}, temp={temp}, corner={corner} got an exception"
        )
        logging.error("Simulation is not completed for this run")

    result_df["res_unscaled"] = res_val

    return result_df


def run_sims(df: pd.DataFrame, dirpath: str, device: str) -> pd.DataFrame:
    """
    Function to run all simulations for all data points and generating results in proper format.

    Parameters
    ----------
    df : pd.DataFrame
        Data frame contains all points will be used in simulation
    dirpath : str or Path
        Output directory for the regresion results
    device: str
        Name of device for the current run
    Returns
    -------
    df: Pd.DataFrame
        Dataframe contains all simulation results
    """

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers_count) as executor:
        futures_list = []
        for j, row in df.iterrows():
            futures_list.append(
                executor.submit(
                    run_sim,
                    dirpath,
                    device,
                    row["width"],
                    row["length"],
                    row["corner"],
                    row["temp"],
                    row["voltage"],
                )
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logging.info("Test case generated an exception: %s" % (exc))

    df = pd.DataFrame(results)
    df = df[
        ["device", "corner", "length", "width", "voltage", "temp", "res_unscaled"]
    ]
    df["res"] = df["res_unscaled"] * df["width"] / df["length"]

    return df


def main():
    """
    Main function for Fets regression for GF180MCU models
    """

    ## Check ngspice version
    check_ngspice_version()

    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)
    pd.options.mode.chained_assignment = None

    main_regr_dir = "res_r_regr"

    devices = [
        "nplus_u",
        "pplus_u",
        "nplus_s",
        "pplus_s",
        "npolyf_u",
        "ppolyf_u",
        "npolyf_s",
        "ppolyf_s",
        "ppolyf_u_1k",
        "ppolyf_u_2k",
        "ppolyf_u_1k_6p0",
        "ppolyf_u_2k_6p0",
        "ppolyf_u_3k",
        "rm1",
        "rm2",
        "rm3",
        "tm6k",
        "tm9k",
        "tm11k",
        "tm30k",
        "nwell",
    ]

    # Simulate all data points for each device
    for dev in devices:
        dev_path = os.path.join(main_regr_dir, dev)

        # Making sure to remove old runs
        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(dev_path, exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {dev}")

        # Loading measured data to be compared
        meas_data_path_wl = f"../../180MCU_SPICE_DATA_clean/gf180mcu_data/RES_r/{dev}_res_wl_meas.csv"
        meas_data_path_temp = f"../../180MCU_SPICE_DATA_clean/gf180mcu_data/RES_r/{dev}_res_temp_meas.csv"

        if not os.path.exists(meas_data_path_wl) or not os.path.isfile(meas_data_path_wl):
            logging.error("There is no measured data to be used in simulation, please recheck")
            logging.error(f"{meas_data_path_wl} file doesn't exist, please recheck")
            exit(1)

        if not os.path.exists(meas_data_path_temp) or not os.path.isfile(meas_data_path_temp):
            logging.error("There is no measured data to be used in simulation, please recheck")
            logging.error(f"{meas_data_path_temp} file doesn't exist, please recheck")
            exit(1)

        meas_df_wl = pd.read_csv(meas_data_path_wl)
        meas_df_temp = pd.read_csv(meas_data_path_temp)
        meas_df = pd.concat([meas_df_wl, meas_df_temp])
        meas_df.drop_duplicates(inplace=True)

        logging.info(f"# Device {dev} number of measured datapoints: {len(meas_df)} ")

        # Simulating all data points
        sim_df = run_sims(meas_df, dev_path, dev)
        sim_df.drop_duplicates(inplace=True)

        logging.info(f"# Device {dev} number of simulated datapoints: {len(sim_df)} ")

        # Merging meas and sim dataframe in one
        full_df = meas_df.merge(sim_df,
                                on=['device', 'corner', 'length', 'width', 'voltage', 'temp'],
                                how='left',
                                suffixes=('_meas', '_sim'))

        # Error calculation and report
        ## Relative error calculation for RES-r
        full_df["res_err"] = np.abs((full_df["res_meas"] - full_df["res_sim"]) * 100.0 / (full_df["res_meas"]))
        full_df.to_csv(f"{dev_path}/{dev}_full_merged_data.csv", index=False)

        # Calculate Q [quantile] to verify matching between measured and simulated data
        ## Refer to https://builtin.com/data-science/boxplot for more details.
        q_target = full_df["res_err"].quantile(QUANTILE_RATIO)
        logging.info(f"Quantile target for {dev} device is: {q_target} %")

        bad_err_full_df_loc = full_df[full_df["res_err"] > PASS_THRESH]
        bad_err_full_df = bad_err_full_df_loc[(bad_err_full_df_loc["res_sim"] >= MAX_VAL_DETECT) | (bad_err_full_df_loc["res_err"] >= MAX_VAL_DETECT)]
        bad_err_full_df.to_csv(f"{dev_path}/{dev}_r_bad_err.csv", index=False)
        logging.info(f"Bad relative errors between measured and simulated data at {dev}_r_bad_err.csv")

        # calculating the relative error of each device and reporting it
        min_error_total = float(full_df["res_err"].min())
        max_error_total = float(full_df["res_err"].max())
        mean_error_total = float(full_df["res_err"].mean())

        # Cliping relative error at 100%
        min_error_total = 100 if min_error_total > 100 else min_error_total
        max_error_total = 100 if max_error_total > 100 else max_error_total
        mean_error_total = 100 if mean_error_total > 100 else mean_error_total

        # logging relative error
        logging.info(
            f"# Device {dev} R min error: {min_error_total:.2f} %, max error: {max_error_total:.2f} %, mean error {mean_error_total:.2f} %"
        )

        # Verify regression results
        if q_target <= PASS_THRESH:
            logging.info(f"# Device {dev} for R simulation has passed regression.")
        else:
            logging.error(
                f"# Device {dev}-R simulation has failed regression. Needs more analysis."
            )
            logging.error(
                f"#Failed regression for {dev}-R analysis."
            )
            exit(1)

# ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================


if __name__ == "__main__":

    # Args
    arguments = docopt(__doc__, version="MODELS-REGRESSION: 0.2")
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
