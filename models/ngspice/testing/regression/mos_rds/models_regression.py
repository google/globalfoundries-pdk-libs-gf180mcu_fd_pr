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
  models_regression.py [--num_cores=<num>] [--meas_result=<meas_result>]

  -h, --help                     Show help text.
  -v, --version                  Show version.
  --num_cores=<num>              Number of cores to be used by simulator
  --meas_result=<meas_result>    Select measurement output to be tested (Allowed values for Fets are id, rds). [default: rds]
"""

from docopt import docopt
import pandas as pd
import numpy as np
from subprocess import check_call
from jinja2 import Template
import concurrent.futures
import shutil
import multiprocessing as mp
import glob
import os
import logging
import re

# CONSTANT VALUES
PASS_THRESH = 5.0
# === ID MEAS ===
MAX_VAL_DETECT_ID = 20.0e-6
CLIP_CURR = 10e-12  # lowest curr to clip on
QUANTILE_ID = 0.98
# === RDS MEAS ===
MAX_VAL_DETECT_RDS = 10e3
QUANTILE_RDS = 0.95


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
        logging.info(f"Your ngspice version is: ngspice {version}")

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
    return check_call(f"ngspice -b {netlist_path} -o {netlist_path}.log > {netlist_path}.log 2>&1", shell=True)


def run_sim(dirpath: str, device: str, meas_out_result: str,
            width: str, length: float, corner: float,
            temp: float, const_var: str, const_var_val: float,
            sweeps: str) -> dict:
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
    const_var: str
        Name of constant voltage for the current run
    const_var_val: float
        Value of constant voltage for the current run
    sweeps: str
        Str that holds all voltage sweeps for the current run
    Returns
    -------
    info(dict):
        Dataframe contains results for the current run
    """

    # Get model card path
    regression_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.dirname(os.path.dirname(os.path.dirname(regression_dir)))
    model_card_path = os.path.join(models_dir, "sm141064.ngspice")
    model_design_path = os.path.join(models_dir, "design.ngspice")

    # Select desired nelist templete to be used in the current run
    if meas_out_result == "id":
        device_group_netlist = "nfet" if "nfet" in device else "pfet"
    else:
        if "03v3" in device:
            device_group_netlist = "nfet_03v3" if "nfet" in device else "pfet_03v3"
        elif "06v0_nvt" in device:
            device_group_netlist = "nfet_06v0_nvt"
        else:
            device_group_netlist = "nfet_06v0" if "nfet" in device else "pfet_06v0"

    netlist_tmp = os.path.join(f"device_netlists_{meas_out_result}", f"{device_group_netlist}.spice")

    # Preparing output directory at which results will be added
    dev_netlists_path = os.path.join(dirpath, f"{device}_netlists")
    os.makedirs(dev_netlists_path, exist_ok=True)

    sp_file_name = f"netlist_w{width}_l{length}_t{temp}_{const_var}{const_var_val}_{meas_out_result}.spice"
    netlist_path = os.path.join(dev_netlists_path, sp_file_name)

    sim_file_name = f"simulated_w{width}_l{length}_t{temp}_{const_var}{const_var_val}_{meas_out_result}.csv"
    result_path = os.path.join(dev_netlists_path, sim_file_name)

    info = {}
    info["device"] = device
    info["temp"] = temp
    info["corner"] = corner
    info["length"] = length
    info["width"] = width

    # Check constant voltage values
    vbs_val = const_var_val if const_var == "vbs" else 0
    vds_val = const_var_val if const_var == "vds" else 6

    # Generating netlist templates for all variations
    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device,
                    meas_out_result=meas_out_result,
                    width=width,
                    length=length,
                    temp=temp,
                    corner=corner,
                    sweeps=sweeps,
                    vds_val=vds_val,
                    vbs_val=vbs_val,
                    const_var=const_var,
                    const_var_val=const_var_val,
                    result_path=result_path,
                    model_card_path=model_card_path,
                    model_design_path=model_design_path,
                )
            )

    # Running ngspice for each netlist
    logging.info(f"Running simulation for {device} at w={width}, l={length}, temp={temp}, sweeps={sweeps}, out={meas_out_result}")

    # calling simulator to run netlist and write its results
    try:
        simulate_device(netlist_path)
        mos_id_rd = result_path if os.path.exists(result_path) else "None"
    except Exception:
        mos_id_rd = "None"

    # Cleaning output csv files from simulation results and
    ## fromating columns to match what we have in measurement
    if os.path.exists(result_path) and os.path.isfile(result_path):
        result_df = pd.read_csv(result_path, delimiter=r"\s+")
        # Drop unwanted columns for simplicity
        result_df.drop("v-sweep", axis=1, inplace=True)

        # Adding columns for all variations per each run
        result_df["W (um)"] = width
        result_df["L (um)"] = length
        result_df["corner"] = corner
        result_df["temp"] = temp

        # Writing output in clean format in same csv path of resutls
        result_df.to_csv(result_path, index=False, header=True, sep=",")

    info["id_rds_sim"] = mos_id_rd

    return info


def run_sims(
    df: pd.DataFrame, dirpath: str, device: str, meas_out_result: str,
) -> pd.DataFrame:
    """
    Function to run all simulations for all data points and generating results in proper format.

    Parameters
    ----------
    df : pd.DataFrame
        Data frame contains all sweep points will be used in simulation
    dirpath : str or Path
        Output directory for the regresion results
    device: str
        Name of device for the current run
    meas_out_result: str
        Measurement selected to be test for the current regression.
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
                    meas_out_result,
                    row["W (um)"],
                    row["L (um)"],
                    row["corner"],
                    row["temp"],
                    row["const_var"],
                    row["const_var_val"],
                    row["sweeps"],
                )
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logging.info("Test case generated an exception: %s" % (exc))

    # Get all simulation generated csv files
    results_path = os.path.join(dirpath, f"{device}_netlists")
    run_results_csv = glob.glob(f"{results_path}/*.csv")

    # Merging all simulation results in one dataframe
    df = pd.concat([pd.read_csv(f) for f in run_results_csv], ignore_index=True)
    return df


def main(meas_out_result):
    """
    Main function for Fets regression for GF180MCU models
    Parameters
    ----------
    meas_out_result : str
        Measurement selected to be test for the current regression.
    """

    ## Check ngspice version
    check_ngspice_version()

    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)
    pd.options.mode.chained_assignment = None

    main_regr_dir = "run_mos_id_rds_regr"

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

    # Simulate all data points for each device
    for dev in devices:
        dev_path = os.path.join(main_regr_dir, dev)

        # Making sure to remove old runs
        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(dev_path, exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {dev}")

        # Loading sweep file used in measurements to be used in simulation for regression
        sweeps_file = f"../../../../180MCU_SPICE_DATA_clean/gf180mcu_data/MOS_iv/{dev}_sweeps_{meas_out_result}.csv"

        if not os.path.exists(sweeps_file) or not os.path.isfile(sweeps_file):
            logging.error("There is no measured data to be used in simulation, please recheck")
            logging.error(f"{sweeps_file} file doesn't exist, please recheck")
            exit(1)

        df_sweeps = pd.read_csv(sweeps_file)
        logging.info(f"Data points used in simulation for {dev}:\n {df_sweeps}")

        sim_df = run_sims(df_sweeps, dev_path, dev, meas_out_result)
        # Round all voltages to elimniate using long digits that could cause mismatch with meas df
        ## Simulator uses small values instead of 0 [10e-16 for example]
        sim_df = sim_df.round({'vbs': 2, 'vgs': 2, 'vds': 2})
        sim_df.drop_duplicates(inplace=True)

        logging.info(f"# Device {dev} number of simulated datapoints for {meas_out_result} : {len(sim_df)} ")

        # Loading measured data to be compared
        meas_data_path = f"../../../../180MCU_SPICE_DATA_clean/gf180mcu_data/MOS_iv/{dev}_meas_{meas_out_result}.csv"

        if not os.path.exists(meas_data_path) or not os.path.isfile(meas_data_path):
            logging.error("There is no measured data to be used in simulation, please recheck")
            logging.error(f"{meas_data_path} file doesn't exist, please recheck")
            exit(1)

        meas_df = pd.read_csv(meas_data_path)
        meas_df = meas_df.round({'vbs': 2, 'vgs': 2, 'vds': 2})
        meas_df.drop_duplicates(inplace=True)

        logging.info(f"# Device {dev} number of measured datapoints for {meas_out_result} : {len(meas_df)} ")

        # Merging meas and sim dataframe in one
        full_df = meas_df.merge(sim_df,
                                on=['W (um)', 'L (um)', 'corner', 'temp', 'vds', 'vgs', 'vbs'],
                                how='left',
                                suffixes=('_meas', '_sim'))

        # Clipping current values to lowest curr
        if meas_out_result == "id":
            full_df['id_meas'] = full_df['id_meas'].clip(lower=CLIP_CURR)
            full_df['id_sim'] = full_df['id_sim'].clip(lower=CLIP_CURR)

        # Droping first/last row for Rds measurement [first/last simulation point]
        ## as we have measured Rds as a partial derivative of vds to ids.
        ## As each point is related to next point, so last point have no next point so its calculated value isn't correct.
        if meas_out_result == 'rds':
            full_df = full_df[~full_df['vds'].isin([0.0, -0.0])]  # Either nfet or pfet
            if '03v3' in dev:
                # Last simlulation points for 03v3 devices for Rds measurements at Vds = 3.3V
                full_df = full_df[~full_df['vds'].isin([3.3, -3.3])]  # Either nfet or pfet
            else:
                # Last simlulation points for 03v3 devices for Rds measurements at Vds = 6.6V
                full_df = full_df[~full_df['vds'].isin([6.6, -6.6])]  # Either nfet or pfet

        # Error calculation and report
        ## Relative error calculation for FETs
        full_df[f"{meas_out_result}_err"] = np.abs((full_df[f"{meas_out_result}_meas"] - full_df[f"{meas_out_result}_sim"]) * 100.0 / full_df[f"{meas_out_result}_meas"])
        full_df.to_csv(f"{dev_path}/{dev}_full_merged_data.csv", index=False)

        # Calculate Q [quantile] to verify matching between measured and simulated data
        ## Refer to https://builtin.com/data-science/boxplot for more details.
        quantile_val = QUANTILE_ID if meas_out_result == 'id' else QUANTILE_RDS
        max_val_detect = MAX_VAL_DETECT_ID if meas_out_result == 'id' else MAX_VAL_DETECT_RDS

        q_target = full_df[f"{meas_out_result}_err"].quantile(quantile_val)
        logging.info(f"Quantile target for {dev} device is: {q_target} %")

        bad_err_full_df_loc = full_df[full_df[f"{meas_out_result}_err"] > PASS_THRESH]
        bad_err_full_df = bad_err_full_df_loc[(bad_err_full_df_loc[f"{meas_out_result}_sim"] >= max_val_detect) | (bad_err_full_df_loc[f"{meas_out_result}_meas"] >= max_val_detect)]
        bad_err_full_df.to_csv(f"{dev_path}/{dev}_bad_err_{meas_out_result}.csv", index=False)
        logging.info(f"Bad relative errors between measured and simulated data at {dev}_bad_err_{meas_out_result}.csv")

        # calculating the relative error of each device and reporting it
        min_error_total = float(full_df[f"{meas_out_result}_err"].min())
        max_error_total = float(full_df[f"{meas_out_result}_err"].max())
        mean_error_total = float(full_df[f"{meas_out_result}_err"].mean())

        # Cliping relative error at 100%
        min_error_total = 100 if min_error_total > 100 else min_error_total
        max_error_total = 100 if max_error_total > 100 else max_error_total
        mean_error_total = 100 if mean_error_total > 100 else mean_error_total

        # logging relative error
        logging.info(
            f"# Device {dev} {meas_out_result} min error: {min_error_total:.2f} %, max error: {max_error_total:.2f} %, mean error {mean_error_total:.2f} %"
        )

        # Verify regression results
        if q_target <= PASS_THRESH:
            logging.info(f"# Device {dev} for {meas_out_result} simulation has passed regression.")
        else:
            logging.error(
                f"# Device {dev} {meas_out_result} simulation has failed regression. Needs more analysis."
            )
            logging.error(
                f"#Failed regression for {dev}-{meas_out_result} analysis."
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

    meas_out_result = arguments["--meas_result"]

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            logging.StreamHandler(),
        ],
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    if meas_out_result not in ["id", "rds"]:
        logging.error(f"{meas_out_result} is not supported, allowed measurements for Fets are [id, rds], please recheck")
        exit(1)

    # Calling main function
    main(meas_out_result)
