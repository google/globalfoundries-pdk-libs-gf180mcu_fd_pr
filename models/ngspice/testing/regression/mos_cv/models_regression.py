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
from subprocess import check_call
from jinja2 import Template
import concurrent.futures
import shutil
import multiprocessing as mp
import glob
import os
import logging


# CONSTANT VALUES
PASS_THRESH = 5.0
MAX_VAL_DETECT = 10 # 10fF
CLIP_CURR = 10e-12  # lowest curr to clip on
TOLE = 0.001


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
    return check_call(f"ngspice -b {netlist_path} -o {netlist_path}.log > {netlist_path}.log 2>&1", shell=True)


def run_sim(dirpath: str, device: str, cap: str,
            width: str, length: float, nf:int,
            corner: float, temp: float, const_var: str,
            const_var_val: float, sweeps: str) -> dict:
    """
    Function to run simulation for all data points per each variation.

    Parameters
    ----------
    dirpath : str or Path
        Path to the run results directory
    device : str
        Device used in regression test
    cap: str
        Measured capacitance for the current regression.        
    width: float
        Width value for the current run
    length: float
        length value for the current run
   nf: int
        Number of fingers for FETs used in the current run        
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

    # Select desired nelist templete to be used in the current run
    netlist_tmp = os.path.join(f"device_netlists", f"fet_{cap}.spice")

    # Preparing output directory at which results will be added
    dev_path = os.path.join(dirpath, device)
    dev_netlists_path = os.path.join(dev_path, f"{device}_netlists")
    os.makedirs(dev_netlists_path, exist_ok=True)

    sp_file_name = f"netlist_w{width}_l{length}_nf{nf}_t{temp}_{const_var}{const_var_val}_{cap}.spice"
    netlist_path = os.path.join(dev_netlists_path, sp_file_name)

    sim_file_name = f"simulated_w{width}_l{length}_nf{nf}_t{temp}_{const_var}{const_var_val}_{cap}.csv"
    result_path = os.path.join(dev_netlists_path, sim_file_name)

    info = {}
    info["device"] = device
    info["temp"] = temp
    info["corner"] = corner
    info["length"] = length
    info["width"] = width
    info["nf"] = nf

    # Check constant voltage values
    vbs_val = const_var_val if const_var == "vbs" else 0
    vds_val = const_var_val if const_var == "vds" else 6

    # Formating sweeps to be valid for our template
    tole = 0 if cap == 'cgg' else TOLE
    main_sweep = " ".join(sweeps.split(" ")[:4])
    second_sweep = " ".join(sweeps.split(" ")[4:])
    second_sweep_volt = second_sweep.split(" ")[0]
    second_sweep_start = float(second_sweep.split(" ")[1])
    second_sweep_stop = float(second_sweep.split(" ")[2]) + tole
    second_sweep_step = float(second_sweep.split(" ")[3])

    # Generating netlist templates for all variations
    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device,
                    width=width,
                    length=length,
                    nf=nf,
                    temp=temp,
                    cap=cap,
                    main_sweep=main_sweep,
                    second_sweep_volt=second_sweep_volt,
                    second_sweep_start=second_sweep_start,
                    second_sweep_stop=second_sweep_stop,
                    second_sweep_step=second_sweep_step,
                    vds_val=vds_val,
                    vbs_val=vbs_val,
                    const_var=const_var,
                    const_var_val=const_var_val,
                    result_path=result_path,
                )
            )

    # Running ngspice for each netlist
    logging.info(f"Running simulation for {device} at w={width}, l={length}, temp={temp}, sweeps={sweeps}, out={cap}")

    # calling simulator to run netlist and write its results
    try:
        simulate_device(netlist_path)
        mos_id_rd = result_path if os.path.exists(result_path) else np.nan
    except Exception:
        mos_id_rd = np.nan

    # Cleaning output csv files from simulation results and
    ## fromating columns to match what we have in measurement
    if os.path.exists(result_path) and os.path.isfile(result_path):
        result_df = pd.read_csv(result_path, delimiter=r"\s+")
        result_df = result_df[result_df.iloc[:, 0] != result_df.columns[0]]

        # Drop unwanted columns for simplicity
        result_df.drop("v-sweep", axis=1, inplace=True)

        # Adding columns for all variations per each run
        result_df["device_name"] = device
        result_df["W (um)"] = width
        result_df["L (um)"] = length
        result_df["nf"] = nf
        result_df["corner"] = corner
        result_df["temp"] = temp

        # Writing output in clean format in same csv path of resutls
        result_df.to_csv(result_path, index=False, header=True, sep=",")

    info["cv_sim"] = mos_id_rd

    return info


def run_sims(
    df: pd.DataFrame, dirpath: str, device: str, cap: str,
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
    cap: str
        Measured capacitance selected to be test for the current regression.
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
                    cap,
                    row["W (um)"],
                    row["L (um)"],
                    row["nf"],
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
    results_path = os.path.join(dirpath, "*", "*_netlists")
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

    main_regr_dir = "mos_cv_regr"

    devices = [
        "fet_03v3",      # For both types [nfet, pfet]
        "fet_03v3_dss",  # For both types [nfet, pfet]
        "fet_06v0",      # For both types [nfet, pfet]
        "fet_06v0_dss",  # For both types [nfet, pfet]
        "fet_03v3_nvt",  # For both types [nfet, pfet]
    ]

    # Types of measured parasitic caps
    # caps = ['cgc', 'cgg', 'cgs', 'cgd']
    caps = ['cgg', 'cgs', 'cgd']

    # Simulate all data points for each device
    for dev in devices:
        for cap in caps:
            dev_path = os.path.join(main_regr_dir, dev, cap)

            # Making sure to remove old runs
            if os.path.exists(dev_path) and os.path.isdir(dev_path):
                shutil.rmtree(dev_path)

            os.makedirs(dev_path, exist_ok=False)

            logging.info("######" * 10)
            logging.info(f"# Checking Device {dev}")

            # Loading sweep file used in measurements to be used in simulation for regression
            sweeps_file = f"../../180MCU_SPICE_DATA_clean/gf180mcu_data/MOS_cv/{dev}_sweeps_{cap}.csv"

            if not os.path.exists(sweeps_file) or not os.path.isfile(sweeps_file):
                logging.error("There is no measured data to be used in simulation, please recheck")
                logging.error(f"{sweeps_file} file doesn't exist, please recheck")
                exit(1)

            df_sweeps = pd.read_csv(sweeps_file)
            logging.info(f"Data points used in simulation for {dev}:\n {df_sweeps}")

            # Running simulation for all data points
            sim_df = run_sims(df_sweeps, dev_path, dev, cap)

            # Round all voltages to elimniate using long digits that could cause mismatch with meas df
            ## Simulator uses small values instead of 0 [10e-16 for example]
            sim_df = sim_df.round({'vbs': 2, 'vgs': 2, 'vds': 2})
            sim_df.drop_duplicates(inplace=True)
            sim_df.to_csv("test.csv", index=False)
            logging.info(f"# Device {dev} number of simulated datapoints for {cap} : {len(sim_df)} ")

            # Loading measured data to be compared
            meas_data_path = f"../../180MCU_SPICE_DATA_clean/gf180mcu_data/MOS_cv/{dev}_meas_{cap}.csv"

            if not os.path.exists(meas_data_path) or not os.path.isfile(meas_data_path):
                logging.error("There is no measured data to be used in simulation, please recheck")
                logging.error(f"Data file at {meas_data_path} doesn't exist, please recheck")
                exit(1)

            meas_df = pd.read_csv(meas_data_path)
            meas_df = meas_df.round({'vbs': 2, 'vgs': 2, 'vds': 2})
            meas_df.drop_duplicates(inplace=True)

            logging.info(f"# Device {dev} number of measured datapoints for {cap} : {len(meas_df)} ")

            # Merging meas and sim dataframe in one
            full_df = meas_df.merge(sim_df,
                                    on=['device_name', 'W (um)', 'L (um)', 'nf',
                                        'corner', 'temp', 'vds', 'vgs', 'vbs'],
                                    how='left',
                                    suffixes=('_meas', '_sim'))

            # Error calculation and report
            ## Relative error calculation for fets
            full_df[f"{cap}_err"] = np.abs(full_df[f"{cap}_meas"] - full_df[f"{cap}_sim"]) * 100.0 / (full_df[f"{cap}_meas"])
            full_df.to_csv(f"{dev_path}/{dev}_full_merged_data_{cap}.csv", index=False)

            # Calculate Q [quantile] to verify matching between measured and simulated data
            ## Refer to https://builtin.com/data-science/boxplot for more details.
            q_target = full_df[f"{cap}_err"].quantile(0.98)
            logging.info(f"Quantile target for {dev} device is: {q_target} %")

            bad_err_full_df_loc = full_df[full_df[f"{cap}_err"] > PASS_THRESH]
            bad_err_full_df = bad_err_full_df_loc[(bad_err_full_df_loc[f"{cap}_sim"] >= MAX_VAL_DETECT) | (bad_err_full_df_loc[f"{cap}_meas"] >= MAX_VAL_DETECT)]
            bad_err_full_df.to_csv(f"{dev_path}/{dev}_bad_err_{cap}.csv", index=False)
            logging.info(f"Bad relative errors between measured and simulated data at {dev}_bad_err_{cap}.csv")

            # calculating the relative error of each device and reporting it
            min_error_total = float(full_df[f"{cap}_err"].min())
            max_error_total = float(full_df[f"{cap}_err"].max())
            mean_error_total = float(full_df[f"{cap}_err"].mean())

            # Cliping relative error at 100%
            min_error_total = 100 if min_error_total > 100 else min_error_total
            max_error_total = 100 if max_error_total > 100 else max_error_total
            mean_error_total = 100 if mean_error_total > 100 else mean_error_total

            # logging relative error
            logging.info(
                f"# Device {dev} {cap} min error: {min_error_total:.2f} %, max error: {max_error_total:.2f} %, mean error {mean_error_total:.2f} %"
            )

            # Verify regression results
            if q_target <= PASS_THRESH:
                logging.info(f"# Device {dev} for {cap} simulation has passed regression.")
            else:
                logging.error(
                    f"# Device {dev} {cap} simulation has failed regression. Needs more analysis."
                )
                logging.error(
                    f"#Failed regression for {dev}-{cap} analysis."
                )
                # exit(1)  # TODO: Check high errors for Caps measurements

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
