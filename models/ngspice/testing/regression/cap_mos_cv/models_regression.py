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
import warnings

# CONSTANT VALUES
RES_MOSCAP = 100   # We will use this res (kohm) in RC circuit for MOSCAP measurement
PASS_THRESH = 5.0  # Threshold value that will be used to test our regression
MAX_VAL_DETECT = 10.0e-15
CLIP_CAP = 200e-15  # lowest curr to clip on
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


def run_sim(dirpath: str, device_name: str, width: str,
            length: float, corner: float, temp: float,
            cj_max: float, sweep: str) -> dict:
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
    cj_max: float
        Max cap value in measured data for this device
    sweep: str
        Voltage sweep will be used during simulation
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

    netlist_tmp = os.path.join("device_netlists", "cap_mos.spice")

    # Preparing output directory at which results will be added
    dev_netlists_path = os.path.join(dirpath, f"{device_name}_netlists")
    os.makedirs(dev_netlists_path, exist_ok=True)

    sp_file_name = f"netlist_w{width}_l{length}_t{temp}_{corner}.spice"
    netlist_path = os.path.join(dev_netlists_path, sp_file_name)

    sim_file_pos = f"simulated_w{width}_l{length}_t{temp}_{corner}_pos.tsv"
    sim_file_neg = f"simulated_w{width}_l{length}_t{temp}_{corner}_neg.tsv"
    sim_file = f"simulated_w{width}_l{length}_t{temp}_{corner}.csv"
    result_path_pos = os.path.join(dev_netlists_path, sim_file_pos)
    result_path_neg = os.path.join(dev_netlists_path, sim_file_neg)
    result_path = os.path.join(dev_netlists_path, sim_file)

    # Extactng main values used in all sim for same device
    ## Sweep variable in this format: Vj {min} {max} {step}
    ## We will use supply voltage with double max voltage value,
    ## to make sure that the cap is fully charged.
    min_volt_sweep = float(sweep.split(" ")[1])
    max_volt_sweep = float(sweep.split(" ")[2])
    step_volt_sweep = float(sweep.split(" ")[3])

    # We will get our cap value at 4*time_const [4*R*C]
    ## R * C = kohm * fF = ps
    sim_run_time = round(4 * float(RES_MOSCAP * cj_max))

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
                    supp_val=max_volt_sweep,
                    res_val=RES_MOSCAP,
                    sim_run_time=sim_run_time,
                    result_path_pos=result_path_pos,
                    result_path_neg=result_path_neg,
                    model_card_path=model_card_path,
                    model_design_path=model_design_path,
                )
            )

    # Running ngspice for each netlist
    logging.info(f"Running simulation for {device_name}-cv at w={width}, l={length}, temp={temp}, corner={corner}")

    # calling simulator to run netlist and write its results
    simulate_device(netlist_path)

    # check if pos sim data is generated
    if not os.path.exists(result_path_pos) or not os.path.isfile(result_path_pos):
        logging.error(f"Running simulation for {device_name}-cv at w={width}, l={length}, temp={temp}, corner={corner} got an exception")
        logging.error("Simulation is not completed for this run")
        exit(1)

    # check if neg sim data is generated
    if not os.path.exists(result_path_neg) or not os.path.isfile(result_path_neg):
        logging.error(f"Running simulation for {device_name}-cv at w={width}, l={length}, temp={temp}, corner={corner} got an exception")
        logging.error("Simulation is not completed for this run")
        exit(1)

    # Cleaning simulated data and handling its format to be like measured one
    pos_df = pd.read_table(result_path_pos, sep=r"\s+", names=["time", "Vj", "time_1", "q_t"])
    neg_df = pd.read_table(result_path_neg, sep=r"\s+", names=["time", "Vj", "time_1", "q_t"])
    pos_df.drop(columns=["time_1"], inplace=True)
    neg_df.drop(columns=["time_1"], inplace=True)
    full_df = pd.concat([pos_df, neg_df])

    # Calc. cap value (fF) form given Q (charge) and V (voltage)
    full_df["Cj"] = np.abs(np.gradient(full_df["q_t"], full_df["Vj"]) / 1.0e-15)
    full_df = full_df[full_df['Vj'] <= max_volt_sweep]
    full_df = full_df[full_df['Vj'] >= min_volt_sweep]
    full_df.sort_values(by='Vj', inplace=True)
    full_df.drop(columns=['time', 'q_t'], inplace=True)

    # Construct final simulated data frame
    sim_df = pd.DataFrame()
    sim_df['Vj'] = np.arange(min_volt_sweep, max_volt_sweep + step_volt_sweep, step_volt_sweep)
    sim_df = pd.merge_asof(sim_df, full_df, on="Vj", direction="nearest")
    sim_df["device_name"] = device_name
    sim_df["W (um)"] = width
    sim_df["L (um)"] = length
    sim_df["corner"] = corner
    sim_df["temp"] = temp
    sim_df = sim_df.round({'Vj': 2})

    sim_df.to_csv(result_path, index=False)

    return sim_df


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
                    row["cj_max"],
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

    main_regr_dir = "run_cap_mos_cv_regr"

    devices = [
        "cap_mos_03v3",  # All types [cap_nmos, cap_pmos, cap_nmos_b, cap_pmos_b]
        "cap_mos_06v0",  # All types [cap_nmos, cap_pmos, cap_nmos_b, cap_pmos_b]
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
        meas_data_path = f"../../../../180MCU_SPICE_DATA_clean/gf180mcu_data/MOSCAP_cv/{dev}_meas_cv.csv"

        if not os.path.exists(meas_data_path) or not os.path.isfile(meas_data_path):
            logging.error("There is no measured data to be used in simulation, please recheck")
            logging.error(f"{meas_data_path} file doesn't exist, please recheck")
            exit(1)

        meas_df = pd.read_csv(meas_data_path)
        meas_df.drop_duplicates(inplace=True)

        logging.info(f"# Device {dev} number of measured datapoints for cv : {len(meas_df)} ")

        # Loading sweep data that will be used in simulation to get all data points
        sweep_data_path = f"../../../../180MCU_SPICE_DATA_clean/gf180mcu_data/MOSCAP_cv/{dev}_sweeps_cv.csv"

        if not os.path.exists(sweep_data_path) or not os.path.isfile(sweep_data_path):
            logging.error("There is no sweep data to be used in simulation, please recheck")
            logging.error(f"{sweep_data_path} file doesn't exist, please recheck")
            exit(1)

        sweep_df = pd.read_csv(sweep_data_path)
        sweep_df.drop_duplicates(inplace=True)

        logging.info(f"# Device {dev} number of sweep datapoints (runs) for cv : {len(sweep_df)} ")

        sim_df = run_sims(sweep_df, dev_path)
        sim_df.drop_duplicates(inplace=True)

        logging.info(f"# Device {dev} number of simulated datapoints for cv : {len(sim_df)} ")

        # Merging meas and sim dataframe in one
        full_df = meas_df.merge(sim_df,
                                on=['device_name', 'W (um)', 'L (um)', 'corner', 'temp', 'Vj'],
                                how='left',
                                suffixes=('_meas', '_sim'))

        # Error calculation and report
        ## Relative error calculation for fets
        full_df["Cj_err"] = np.abs((full_df["Cj_meas"] - full_df["Cj_sim"]) * 100.0 / (full_df["Cj_meas"]))
        full_df.to_csv(f"{dev_path}/{dev}_full_merged_data.csv", index=False)

        # Calculate Q [quantile] to verify matching between measured and simulated data
        ## Refer to https://builtin.com/data-science/boxplot for more details.
        q_target = full_df["Cj_err"].quantile(QUANTILE_RATIO)
        logging.info(f"Quantile target for {dev} device is: {q_target}")

        bad_err_full_df_loc = full_df[full_df["Cj_err"] > PASS_THRESH]
        bad_err_full_df = bad_err_full_df_loc[(bad_err_full_df_loc["Cj_sim"] >= MAX_VAL_DETECT) | (bad_err_full_df_loc["Cj_meas"] >= MAX_VAL_DETECT)]
        bad_err_full_df.to_csv(f"{dev_path}/{dev}_bad_err_cv.csv", index=False)
        logging.info(f"Bad relative errors between measured and simulated data at {dev}_bad_err_cv.csv")

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
            logging.error(
                f"#Failed regression for {dev}-CV analysis."
            )
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

    warnings.simplefilter(action='ignore', category=RuntimeWarning)

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
