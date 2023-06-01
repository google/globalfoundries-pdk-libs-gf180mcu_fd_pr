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
import re

# CONSTANT VALUES
PASS_THRESH = 5.0
MAX_VAL_DETECT = 0.1e-15  # Max value to detect bad errors 0.1fF
QUANTILE_RATIO = 0.98  # quantile ratio used for regression test


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
        version = int(re.search(r"ngspice-([0-9]+)", ngspice_v_).group(1))
        logging.info(f"Your Klayout version is: ngspice {version}")

        if version <= 37:
            logging.error(
                "ngspice version is not supported. Please use ngspice version 38 or newer."
            )
            exit(1)


def find_mimcap(log_file):
    """
    Function to parse capacitance value from simulation run log.

    Parameters
    ----------
    log_file : str or Path
        Path to the simulation run log file.
    Returns
    -------
        Parsed capacitance value measured in simulation run.
    """

    cmd = 'grep "cj" {} | head -n 1'.format(log_file)
    process = Popen(cmd, shell=True, stdout=PIPE)
    return float(process.communicate()[0][:-1].decode("utf-8").split("=")[1])


def simulate_device(netlist_path: str):
    """
    Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist cir for run.
    Returns:
        int: Return code of the simulation. 0 if success.  Non-zero if failed.
    """
    return check_call(
        f"ngspice -b {netlist_path} -o {netlist_path}.log > {netlist_path}.log 2>&1",
        shell=True,
    )


def run_sim(
    dirpath: str,
    device_name: str,
    width: str,
    length: float,
    corner: float,
    temp: float,
) -> dict:
    """
    Function to run simulation for all data points per each variation.

    Parameters
    ----------
    dirpath : str or Path
        Path to the run results directory
    device_name : str
        Name of Device used in current run
    width: float
        Width value for the current run
    length: float
        length value for the current run
    corner: str
        Corner used in the current run
    temp: float
        temp value for the current run
    Returns
    -------
    result_df: dict
        Dataframe contains results for the current run
    """

    # Get model card path
    regression_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.dirname(os.path.dirname(os.path.dirname(regression_dir)))
    model_card_path = os.path.join(models_dir, "sm141064.ngspice")
    model_design_path = os.path.join(models_dir, "design.ngspice")

    netlist_tmp = os.path.join("device_netlists", "cap_mim.spice")

    # Preparing output directory at which results will be added
    dev_netlists_path = os.path.join(dirpath, f"{device_name}_netlists")
    os.makedirs(dev_netlists_path, exist_ok=True)

    sp_file_name = f"netlist_w{width}_l{length}_t{temp}_{corner}.spice"
    netlist_path = os.path.join(dev_netlists_path, sp_file_name)

    result_df = {}
    result_df["device_name"] = device_name
    result_df["W (um)"] = width
    result_df["L (um)"] = length
    result_df["corner"] = corner
    result_df["temp"] = temp

    # Generating netlist templates for all variations
    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device_name,
                    width=width,
                    length=length,
                    temp=temp,
                    corner=corner,
                    model_card_path=model_card_path,
                    model_design_path=model_design_path,
                )
            )

    # Running ngspice for each netlist
    logging.info(
        f"Running simulation for {device_name}-cv at w={width}, l={length}, temp={temp}, corner={corner}"
    )

    # calling simulator to run netlist and write its results
    try:
        simulate_device(netlist_path)
        # Get Cj value from run log
        try:
            cj_val = find_mimcap(f"{netlist_path}.log")

        except Exception:
            cj_val = np.nan
            logging.error(
                f"Running simulation at w={width}, l={length}, temp={temp}, corner={corner} got an exception"
            )
            logging.error(f"Regression couldn't get the output from {netlist_path}.log")
    except Exception:
        cj_val = np.nan
        logging.error(
            f"Running simulation at w={width}, l={length}, temp={temp}, corner={corner} got an exception"
        )
        logging.error("Simulation is not completed for this run")

    result_df["Cj"] = cj_val

    return result_df


def run_sims(df: pd.DataFrame, dirpath: str) -> pd.DataFrame:
    """
    Function to run all simulations for all data points and generating results in proper format.

    Parameters
    ----------
    df : pd.DataFrame
        Data frame contains all sweep points will be used in simulation
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
                    row["W (um)"],
                    row["L (um)"],
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

    sim_df = pd.DataFrame(results)

    return sim_df


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

    main_regr_dir = "run_cap_mim_cv_regr"

    devices = [
        "m2m3_noshield",  # All types [cap_mim_1f5, cap_mim_1f0, cap_mim_2f0]
        "m3m4_noshield",  # All types [cap_mim_1f5, cap_mim_1f0, cap_mim_2f0]
        "m4m5_noshield",  # All types [cap_mim_1f5, cap_mim_1f0, cap_mim_2f0]
        "m5m6_noshield",  # All types [cap_mim_1f5, cap_mim_1f0, cap_mim_2f0]
    ]

    # Simulate all data points for each device
    for dev in devices:
        dev_path = os.path.join(main_regr_dir, dev)

        # Making sure to remove old runs
        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(dev_path, exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device cap_mim {dev}")

        # Loading measured data to be compared
        meas_data_path = (
            "../../../../180MCU_SPICE_DATA_clean/gf180mcu_data/MIMCAP_cv/cap_mim_meas_cv.csv"
        )

        if not os.path.exists(meas_data_path) or not os.path.isfile(meas_data_path):
            logging.error(
                "There is no measured data to be used in simulation, please recheck"
            )
            logging.error(f"{meas_data_path} file doesn't exist, please recheck")
            exit(1)

        meas_df = pd.read_csv(meas_data_path)

        # For MIMCAP [Metal cap], the cap value is almost same for all voltages.
        ## We will drop voltage column and round cap value (fF) to 2 numbers after digits.
        ## To optimize run time and ignore redundant runs.
        meas_df.drop("Vj", axis=1, inplace=True)
        meas_df = meas_df.round({"Cj": 2})
        meas_df.drop_duplicates(
            subset=["device_name", "W (um)", "L (um)", "corner", "temp"], inplace=True
        )

        logging.info(
            f"# Device cap_mim {dev} number of measured datapoints for cv : {len(meas_df)} "
        )

        # We have 4 types for MIMCAP, all have same data points
        meas_df["device_name"] = meas_df["device_name"] + f"_{dev}"

        # Simulating all data points to be compared with measured ones
        sim_df = run_sims(meas_df, dev_path)
        sim_df.drop_duplicates(inplace=True)

        logging.info(
            f"# Device cap_mim {dev} number of simulated datapoints for cv : {len(sim_df)} "
        )

        # Merging meas and sim dataframe in one
        full_df = meas_df.merge(
            sim_df,
            on=["device_name", "W (um)", "L (um)", "corner", "temp"],
            how="left",
            suffixes=("_meas", "_sim"),
        )

        # Error calculation and report
        ## Relative error calculation for fets
        full_df["Cj_err"] = np.abs((full_df["Cj_meas"] - full_df["Cj_sim"]) * 100.0 / (full_df["Cj_meas"]))
        full_df.to_csv(f"{dev_path}/{dev}_full_merged_data.csv", index=False)

        # Calculate Q [quantile] to verify matching between measured and simulated data
        ## Refer to https://builtin.com/data-science/boxplot for more details.
        q_target = full_df["Cj_err"].quantile(QUANTILE_RATIO)
        logging.info(f"Quantile target for {dev} device is: {q_target}")

        bad_err_full_df_loc = full_df[full_df["Cj_err"] > PASS_THRESH]
        bad_err_full_df = bad_err_full_df_loc[
            (bad_err_full_df_loc["Cj_sim"] >= MAX_VAL_DETECT)
            | (bad_err_full_df_loc["Cj_meas"] >= MAX_VAL_DETECT)
        ]
        bad_err_full_df.to_csv(f"{dev_path}/{dev}_bad_err_cv.csv", index=False)
        logging.info(
            f"Bad relative errors between measured and simulated data at {dev}_bad_err_cv.csv"
        )

        # calculating the relative error of each device and reporting it
        min_error_total = float(full_df["Cj_err"].min())
        max_error_total = float(full_df["Cj_err"].max())
        mean_error_total = float(full_df["Cj_err"].mean())

        # Cliping relative error at 100%
        min_error_total = 100 if min_error_total > 100 else min_error_total
        max_error_total = 100 if max_error_total > 100 else max_error_total
        mean_error_total = 100 if mean_error_total > 100 else mean_error_total

        # logging relative error
        logging.info(
            f"# Device {dev}-cv min error: {min_error_total:.2f} %, max error: {max_error_total:.2f} %, mean error {mean_error_total:.2f} %"
        )

        # Verify regression results
        if q_target <= PASS_THRESH:
            logging.info(f"# Device {dev} for CV simulation has passed regression.")
        else:
            logging.error(
                f"# Device {dev} CV simulation has failed regression. Needs more analysis."
            )
            logging.error(f"#Failed regression for {dev}-CV analysis.")
            exit(1)


# # ================================================================
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
        handlers=[logging.StreamHandler(), ],
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Calling main function
    main()
