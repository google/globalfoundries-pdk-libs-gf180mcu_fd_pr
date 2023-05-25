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
# === BJT-IV ===
MAX_VAL_DETECT = 10e-6  # Max value to detect bad errors above it
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


def run_sim(dirpath: str, device: str, corner: float, temp: float, sweep: str) -> dict:
    """
    Function to run simulation for all data points per each variation.

    Parameters
    ----------
    dirpath : str or Path
        Path to the run results directory
    device : str
        Device used in regression test
    temp: float
        temp value for the current run
    sweep: float
        voltage and current sweep used for the current run
    Returns
    -------
    result_df: dict
        Dataframe contains results for the current run
    """

    # Select desired nelist templete to be used in the current run
    netlist_tmp = os.path.join("device_netlists", "bjt_iv.spice")

    # Preparing output directory at which results will be added
    dev_netlists_path = os.path.join(dirpath, f"{device}_netlists")
    os.makedirs(dev_netlists_path, exist_ok=True)

    sp_file_name = f"netlist_t{temp}_{corner}.spice"
    netlist_path = os.path.join(dev_netlists_path, sp_file_name)

    sim_file_name = f"simulated_t{temp}_{corner}.csv"
    result_path = os.path.join(dev_netlists_path, sim_file_name)

    info = {}
    info["device"] = device
    info["temp"] = temp
    info["corner"] = corner

    # Differientiate between 2 or 3 terminal res
    if "npn" in device:
        terminals = "c b 0 0"
    else:
        terminals = "c b 0"

    # Generating netlist templates for all variations
    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device,
                    terminals=terminals,
                    corner=corner,
                    temp=temp,
                    sweep=sweep,
                    result_path=result_path,
                )
            )

    # Running ngspice for each netlist
    logging.info(f"Running simulation for {device}-iv at temp={temp}, corner={corner}")

    # calling simulator to run netlist and write its results
    try:
        simulate_device(netlist_path)
        bjt_iv = result_path if os.path.exists(result_path) else np.nan
    except Exception:
        bjt_iv = np.nan

    # Cleaning output csv files from simulation results and
    ## fromating columns to match what we have in measurement
    if os.path.exists(result_path) and os.path.isfile(result_path):
        result_df = pd.read_csv(result_path, delimiter=r"\s+")
        # Drop unwanted columns for simplicity
        result_df.drop("v-sweep", axis=1, inplace=True)

        # Adding columns for all variations per each run
        result_df["device_name"] = device
        result_df["corner"] = corner
        result_df["temp"] = temp

        # Writing output in clean format in same csv path of resutls
        result_df.to_csv(result_path, index=False, header=True, sep=",")

    info["ic"] = bjt_iv

    return info


def run_sims(df: pd.DataFrame, dirpath: str) -> pd.DataFrame:
    """
    Function to run all simulations for all data points and generating results in proper format.

    Parameters
    ----------
    df : pd.DataFrame
        Data frame contains all points will be used in simulation
    dirpath : str or Path
        Output directory for the regresion results
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
                    row["device_name"],
                    row["corner"],
                    row["temp"],
                    row["sweep"],
                )
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logging.info("Test case generated an exception: %s" % (exc))

    # Get all simulation generated csv files
    results_path = os.path.join(dirpath, "*_netlists")
    run_results_csv = glob.glob(f"{results_path}/*.csv")

    # Merging all simulation results in one dataframe
    df = pd.concat([pd.read_csv(f) for f in run_results_csv], ignore_index=True)

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

    main_regr_dir = "run_bjt_iv_regr"

    devices = [
        # All npn devices [10p00x10p00, 05p00x05p00, 00p54x16p00, 00p54x08p00, 00p54x04p00, 00p54x02p00]
        "npn",
        # All pnp devices [10p00x00p42, 05p00x00p42, 10p00x10p00, 05p00x05p00]
        "pnp",
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
        meas_data_path = f"../../180MCU_SPICE_DATA_clean/gf180mcu_data/BJT_iv/bjt_{dev}_iv_meas.csv"

        if not os.path.exists(meas_data_path) or not os.path.isfile(meas_data_path):
            logging.error("There is no measured data to be used in simulation, please recheck")
            logging.error(f"{meas_data_path} file doesn't exist, please recheck")
            exit(1)

        meas_df = pd.read_csv(meas_data_path)
        meas_df.drop_duplicates(inplace=True)

        logging.info(f"# Device BJT {dev}-iv number of measured datapoints : {len(meas_df)} ")

        # Loading sweep file used in measurements to be used in simulation for regression
        sweeps_file = f"../../180MCU_SPICE_DATA_clean/gf180mcu_data/BJT_iv/bjt_{dev}_iv_sweeps.csv"

        if not os.path.exists(sweeps_file) or not os.path.isfile(sweeps_file):
            logging.error("There is no measured data to be used in simulation, please recheck")
            logging.error(f"{sweeps_file} file doesn't exist, please recheck")
            exit(1)

        df_sweeps = pd.read_csv(sweeps_file)
        logging.info(f"Data points used in simulation for {dev}:\n {df_sweeps}")

        # Simulating all data points
        sim_df = run_sims(df_sweeps, dev_path)
        sim_df.drop_duplicates(inplace=True)

        logging.info(f"# Device {dev} number of simulated datapoints: {len(sim_df)} ")

        # Merging meas and sim dataframe in one
        full_df = meas_df.merge(sim_df,
                                on=['device_name', 'corner', 'temp', 'ibp' , 'vcp'],
                                how='left',
                                suffixes=('_meas', '_sim'))

        # Error calculation and report
        ## Relative error calculation for BJT-iv
        full_df["ic_err"] = np.abs((full_df["ic_meas"] - full_df["ic_sim"]) * 100.0 / (full_df["ic_meas"]))
        full_df.to_csv(f"{dev_path}/{dev}_full_merged_data.csv", index=False)

        # Calculate Q [quantile] to verify matching between measured and simulated data
        ## Refer to https://builtin.com/data-science/boxplot for more details.
        q_target = full_df["ic_err"].quantile(QUANTILE_RATIO)
        logging.info(f"Quantile target for {dev} device is: {q_target} %")

        bad_err_full_df_loc = full_df[full_df["ic_err"] > PASS_THRESH]
        bad_err_full_df = bad_err_full_df_loc[(bad_err_full_df_loc["ic_sim"] >= MAX_VAL_DETECT) | (bad_err_full_df_loc["ic_err"] >= MAX_VAL_DETECT)]
        bad_err_full_df.to_csv(f"{dev_path}/{dev}_ic_bad_err.csv", index=False)
        logging.info(f"Bad relative errors between measured and simulated data at {dev}_ic_bad_err.csv")

        # calculating the relative error of each device and reporting it
        min_error_total = float(full_df["ic_err"].min())
        max_error_total = float(full_df["ic_err"].max())
        mean_error_total = float(full_df["ic_err"].mean())

        # Cliping relative error at 100%
        min_error_total = 100 if min_error_total > 100 else min_error_total
        max_error_total = 100 if max_error_total > 100 else max_error_total
        mean_error_total = 100 if mean_error_total > 100 else mean_error_total

        # logging relative error
        logging.info(
            f"# Device {dev}-iv min error: {min_error_total:.2f} %, max error: {max_error_total:.2f} %, mean error {mean_error_total:.2f} %"
        )

        # Verify regression results
        if q_target <= PASS_THRESH:
            logging.info(f"# Device {dev}-iv for simulation has passed regression.")
        else:
            logging.error(
                f"# Device {dev}-iv simulation has failed regression. Needs more analysis."
            )
            logging.error(
                f"#Failed regression for {dev}-iv analysis."
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
