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
PASS_THRESH = 5.0  # Threshold value that will be used to test our regression
MAX_VAL_DETECT = 1e-15
CLIP_CURR = 10e-12
QUANTILE_RATIO = 0.95  # quantile ratio used for regression test


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


def run_sim(dirpath: str, device_name: str, area: str,
            perim: float, corner: float, temp: float,
            sweep: str) -> dict:
    """
    Function to run simulation for all data points per each variation.

    Parameters
    ----------
    dirpath : str or Path
        Path to the run results directory
    device_name : str
        Name of Device used in current run
    area: float
        Area value for the current run
    perim: float
        Perimeter value for the current run
    corner: str
        Corner used in the current run
    temp: float
        temp value for the current run
    sweep: str
        Voltage sweep will be used during simulation
    Returns
    -------
    info: Dict
        Dict contains info for the current run
    """

    # Get model card path
    regression_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.dirname(os.path.dirname(os.path.dirname(regression_dir)))
    model_card_path = os.path.join(models_dir, "sm141064.ngspice")
    model_design_path = os.path.join(models_dir, "design.ngspice")

    netlist_tmp = os.path.join("device_netlists", "diode_iv.spice")

    # Preparing output directory at which results will be added
    dev_netlists_path = os.path.join(dirpath, f"{device_name}_netlists")
    os.makedirs(dev_netlists_path, exist_ok=True)

    sp_file_name = f"netlist_A{area}_P{perim}_t{temp}_{corner}.spice"
    netlist_path = os.path.join(dev_netlists_path, sp_file_name)

    sim_file = f"simulated_A{area}_P{perim}_t{temp}_{corner}.csv"
    result_path = os.path.join(dev_netlists_path, sim_file)

    info = {}
    info["device"] = device_name
    info["temp"] = temp
    info["corner"] = corner
    info["Area (pm^2)"] = area
    info["Pj (um)"] = perim

    # Generating netlist templates for all variations
    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device_name,
                    area=area,
                    perim=perim,
                    temp=temp,
                    corner=corner,
                    result_path=result_path,
                    sweep=sweep,
                    model_card_path=model_card_path,
                    model_design_path=model_design_path,
                )
            )

    # Running ngspice for each netlist
    logging.info(f"Running simulation for {device_name}-cv at A={area}p, P={perim}u, temp={temp}, corner={corner}")

    # calling simulator to run netlist and write its results
    simulate_device(netlist_path)

    # calling simulator to run netlist and write its results
    try:
        simulate_device(netlist_path)
        diode_iv = result_path if os.path.exists(result_path) else np.nan
    except Exception:
        diode_iv = np.nan

    # Cleaning output csv files from simulation results and
    ## fromating columns to match what we have in measurement
    if os.path.exists(result_path) and os.path.isfile(result_path):
        result_df = pd.read_csv(result_path, delimiter=r"\s+")
        # Drop unwanted columns for simplicity
        result_df.drop("v-sweep", axis=1, inplace=True)

        # Adding columns for all variations per each run
        result_df["Area (pm^2)"] = area
        result_df["Pj (um)"] = perim
        result_df["corner"] = corner
        result_df["temp"] = temp

        # Writing output in clean format in same csv path of resutls
        result_df.to_csv(result_path, index=False, header=True, sep=",")

    info["diode_id_sim"] = diode_iv

    return info


def run_sims(df: pd.DataFrame, dirpath: str, device_name: str) -> pd.DataFrame:
    """
    Function to run all simulations for all data points and generating results in proper format.

    Parameters
    ----------
    df : pd.DataFrame
        Data frame contains all sweep points will be used in simulation
    dirpath : str or Path
        Output directory for the regresion results
    device_name : str
        Name of Device used in current run
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
                    device_name,
                    row["Area (pm^2)"],
                    row["Pj (um)"],
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
    results_path = os.path.join(dirpath, f"{device_name}_netlists")
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

    main_regr_dir = "run_diode_iv_regr"

    devices = [
        "diode_dw2ps",
        "diode_pw2dw",
        "diode_nd2ps_03v3",
        "diode_nd2ps_06v0",
        "diode_nw2ps_03v3",
        "diode_nw2ps_06v0",
        "diode_pd2nw_03v3",
        "diode_pd2nw_06v0",
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
        meas_data_path = f"../../../../180MCU_SPICE_DATA_clean/gf180mcu_data/diode_iv/{dev}_iv_meas.csv"

        if not os.path.exists(meas_data_path) or not os.path.isfile(meas_data_path):
            logging.error("There is no measured data to be used in simulation, please recheck")
            logging.error(f"{meas_data_path} file doesn't exist, please recheck")
            exit(1)

        meas_df = pd.read_csv(meas_data_path)
        meas_df.drop_duplicates(inplace=True)

        logging.info(f"# Device {dev} number of measured datapoints for cv : {len(meas_df)} ")

        # Loading sweep data that will be used in simulation to get all data points
        sweep_data_path = f"../../../../180MCU_SPICE_DATA_clean/gf180mcu_data/diode_iv/{dev}_iv_sweeps.csv"

        if not os.path.exists(sweep_data_path) or not os.path.isfile(sweep_data_path):
            logging.error("There is no sweep data to be used in simulation, please recheck")
            logging.error(f"{sweep_data_path} file doesn't exist, please recheck")
            exit(1)

        sweep_df = pd.read_csv(sweep_data_path)
        sweep_df.drop_duplicates(inplace=True)

        logging.info(f"# Device {dev} number of sweep datapoints (runs) for cv : {len(sweep_df)} ")

        sim_df = run_sims(sweep_df, dev_path, dev)
        sim_df.drop_duplicates(inplace=True)

        logging.info(f"# Device {dev} number of simulated datapoints for cv : {len(sim_df)} ")

        # Merging meas and sim dataframe in one
        full_df = meas_df.merge(sim_df,
                                on=['Area (pm^2)', 'Pj (um)', 'corner', 'temp', 'Vn'],
                                how='left',
                                suffixes=('_meas', '_sim'))

        # Clipping current values to lowest curr
        # full_df['In_meas'] = full_df['In_meas'].clip(lower=CLIP_CURR)
        # full_df['In_sim'] = full_df['In_sim'].clip(lower=CLIP_CURR)

        # Error calculation and report
        ## Relative error calculation for fets
        full_df["In_err"] = np.abs(full_df["In_meas"] - full_df["In_sim"]) * 100.0 / (full_df["In_meas"])
        full_df.to_csv(f"{dev_path}/{dev}_full_merged_data.csv", index=False)

        # Calculate Q [quantile] to verify matching between measured and simulated data
        ## Refer to https://builtin.com/data-science/boxplot for more details.
        q_target = full_df["In_err"].quantile(QUANTILE_RATIO)
        logging.info(f"Quantile target for {dev} device is: {q_target}")

        bad_err_full_df_loc = full_df[full_df["In_err"] > PASS_THRESH]
        bad_err_full_df = bad_err_full_df_loc[(bad_err_full_df_loc["In_sim"] >= MAX_VAL_DETECT) | (bad_err_full_df_loc["In_meas"] >= MAX_VAL_DETECT)]
        bad_err_full_df.to_csv(f"{dev_path}/{dev}_iv_bad_err.csv", index=False)
        logging.info(f"Bad relative errors between measured and simulated data at {dev}_iv_bad_err.csv")

        # calculating the relative error of each device and reporting it
        min_error_total = float(full_df["In_err"].min())
        max_error_total = float(full_df["In_err"].max())
        mean_error_total = float(full_df["In_err"].mean())

        # Cliping relative error at 100%
        min_error_total = 100 if min_error_total > 100 else min_error_total
        max_error_total = 100 if max_error_total > 100 else max_error_total
        mean_error_total = 100 if mean_error_total > 100 else mean_error_total

        # logging relative error
        logging.info(
            f"# Device {dev}-IV min error: {min_error_total:.2f} %, max error: {max_error_total:.2f} %, mean error {mean_error_total:.2f} %"
        )

        # Verify regression results
        if q_target <= PASS_THRESH:
            logging.info(f"# Device {dev} for IV simulation has passed regression.")
        else:
            logging.error(
                f"# Device {dev} IV simulation has failed regression. Needs more analysis."
            )
            logging.error(
                f"#Failed regression for {dev}-IV analysis."
            )
            # exit(1) #TODO: Investigate for high errors for diode-iv

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
        handlers=[
            logging.StreamHandler(),
        ],
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Calling main function
    main()
