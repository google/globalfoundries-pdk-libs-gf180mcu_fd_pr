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
  --meas_result=<meas_result>    Measurement to be tested (Allowed: id, rds). [default: id]
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
    return check_call(
        f"ngspice -b {netlist_path} -o {netlist_path}.log > {netlist_path}.log 2>&1",
        shell=True)


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
    model_card_path = os.path.join(models_dir, "smbb000149.ngspice")
    model_design_path = os.path.join(models_dir, "design.ngspice")

    # Select desired nelist templete to be used in the current run
    device_group_netlist = "nfet" if "nfet" in device else "pfet"

    netlist_tmp = os.path.join(f"device_netlists_{meas_out_result}",
                               f"{device_group_netlist}.spice")

    # Preparing output directory at which results will be added
    dev_netlists_path = os.path.join(dirpath, f"{device}_netlists")
    os.makedirs(dev_netlists_path, exist_ok=True)

    sp_file_name = \
        f"netlist_w{width}_l{length}_t{temp}_{corner}_{const_var}{const_var_val}_{meas_out_result}.spice"
    netlist_path = os.path.join(dev_netlists_path, sp_file_name)

    sim_file_name = \
        f"simulated_w{width}_l{length}_t{temp}_{corner}_{const_var}{const_var_val}_{meas_out_result}.csv"
    result_path = os.path.join(dev_netlists_path, sim_file_name)

    info = {}
    info["device"] = device
    info["temp"] = temp
    info["corner"] = corner
    info["length"] = length
    info["width"] = width

    # Check constant voltage values
    vbs_val = const_var_val if const_var == "vbs" else 0
    vds_val = const_var_val if const_var == "vds" else 10

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
    logging.info(f"Running simulation for {device} at \
w={width}, l={length}, temp={temp}, sweeps={sweeps}, out={meas_out_result}")

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
        for __j, row in df.iterrows():
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
    Main function for Fets regression for GF180IC models
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

    main_regr_dir = f"run_mos_{meas_out_result}_regr"

    devices = [
        "nfet_10v0_asym",
        "pfet_10v0_asym",
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
        sim_df.drop_duplicates(inplace=True)

        logging.info(f"# Device {dev} number of simulated datapoints for: {meas_out_result} : {len(sim_df)} ")

        sim_df_columns = ["W (um)", "L (um)", "corner", "temp", "vds", "vgs", "vbs", f"{meas_out_result}"]
        sim_df = sim_df.reindex(columns=sim_df_columns)

        sim_df.to_csv(f"{dev_path}/sim_results_{dev}.csv", index=False)

        # Verify regression results
        if not sim_df[f"{meas_out_result}"].isnull().values.any():
            logging.info(f"# Device {dev} for {meas_out_result} simulation has passed.")
        else:
            logging.error(
                f"# Device {dev} {meas_out_result} simulation has failed regression."
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
    arguments = docopt(__doc__, version="MODELS-REGRESSION: 0.1")
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
        logging.error(f"{meas_out_result} is not supported, \
                      allowed measurements for Fets are [id, rds], please recheck")
        exit(1)

    # Calling main function
    main(meas_out_result)
