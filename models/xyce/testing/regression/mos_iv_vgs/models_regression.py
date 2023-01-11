"""
Usage:
  models_regression.py [--num_cores=<num>]

  -h, --help             Show help text.
  -v, --version          Show version.
  --num_cores=<num>      Number of cores to be used by simulator
"""

from re import T
from docopt import docopt
import pandas as pd
import numpy as np
import os
from jinja2 import Template
import concurrent.futures
import shutil
import warnings
import glob
import logging
import multiprocessing as mp

pd.options.mode.chained_assignment = None  # default='warn'
warnings.simplefilter(action="ignore", category=FutureWarning)
NMOS3P3_VGS = [0.8, 1.3, 1.8, 2.3, 2.8, 3.3]
PMOS3P3_VGS = [-0.8, -1.3, -1.8, -2.3, -2.8, -3.3]
NMOS6P0_VGS = [1, 2, 3, 4, 5, 6]
PMOS6P0_VGS = [-1, -2, -3, -4, -5, -6]
NMOS6P0_NAT_VGS = [0.25, 1.4, 2.55, 3.7, 4.85, 6]
PASS_THRESH = 2.0


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    log_file = file_name.replace("-hspice-ext all ", "")
    os.system(f"Xyce {file_name} -l {log_file}.log 2> /dev/null")


def ext_measured(
    dirpath: str, device: str, vds: list[str], vgs: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """ext_measured function calculates get measured data

    Args:
        dirpath(str): measured data path
        device(str): npn or pnp
        vds(list[str]): headers of rest column in the table
        vgs(str): header of first column in the table
    Returns:
        df(DataFrame): output measured df
    """

    # Get dimensions used for each device
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv", usecols=["W (um)", "L (um)"])
    loops = dimensions["L (um)"].count()
    all_dfs = []
    all_dfs1 = []

    # Extracting measured values for each W & L
    for i in range(0, loops * 2, 2):
        # Special case for 1st measured values
        if i == 0:
            # measured Id
            col_list = [
                f"{vds}",
                f"vgs ={vgs[0]}",
                f"vgs ={vgs[1]}",
                f"vgs ={vgs[2]}",
                f"vgs ={vgs[3]}",
                f"vgs ={vgs[4]}",
                f"vgs ={vgs[5]}",
            ]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv", usecols=col_list)
            df_measured.columns = [
                f"{vds}{int(i/2)}",
                f"vgs ={vgs[0]}{int(i/2)}",
                f"vgs ={vgs[1]}{int(i/2)}",
                f"vgs ={vgs[2]}{int(i/2)}",
                f"vgs ={vgs[3]}{int(i/2)}",
                f"vgs ={vgs[4]}{int(i/2)}",
                f"vgs ={vgs[5]}{int(i/2)}",
            ]
            # measured Rds
            col_list = [
                f"{vds}",
                f"vgs ={vgs[0]}.{i+1}",
                f"vgs ={vgs[1]}.{i+1}",
                f"vgs ={vgs[2]}.{i+1}",
                f"vgs ={vgs[3]}.{i+1}",
                f"vgs ={vgs[4]}.{i+1}",
                f"vgs ={vgs[5]}.{i+1}",
            ]
            df_measured1 = pd.read_csv(f"{dirpath}/{device}.csv", usecols=col_list)
            df_measured1.columns = [
                f"{vds}{int(i/2)}",
                f"vgs ={vgs[0]}{int(i/2)}",
                f"vgs ={vgs[1]}{int(i/2)}",
                f"vgs ={vgs[2]}{int(i/2)}",
                f"vgs ={vgs[3]}{int(i/2)}",
                f"vgs ={vgs[4]}{int(i/2)}",
                f"vgs ={vgs[5]}{int(i/2)}",
            ]
        else:
            # measured Id
            col_list = [
                f"{vds}",
                f"vgs ={vgs[0]}.{i}",
                f"vgs ={vgs[1]}.{i}",
                f"vgs ={vgs[2]}.{i}",
                f"vgs ={vgs[3]}.{i}",
                f"vgs ={vgs[4]}.{i}",
                f"vgs ={vgs[5]}.{i}",
            ]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv", usecols=col_list)
            df_measured.columns = [
                f"{vds}{int(i/2)}",
                f"vgs ={vgs[0]}{int(i/2)}",
                f"vgs ={vgs[1]}{int(i/2)}",
                f"vgs ={vgs[2]}{int(i/2)}",
                f"vgs ={vgs[3]}{int(i/2)}",
                f"vgs ={vgs[4]}{int(i/2)}",
                f"vgs ={vgs[5]}{int(i/2)}",
            ]
            # measured Rds
            col_list = [
                f"{vds}",
                f"vgs ={vgs[0]}.{i+1}",
                f"vgs ={vgs[1]}.{i+1}",
                f"vgs ={vgs[2]}.{i+1}",
                f"vgs ={vgs[3]}.{i+1}",
                f"vgs ={vgs[4]}.{i+1}",
                f"vgs ={vgs[5]}.{i+1}",
            ]
            df_measured1 = pd.read_csv(f"{dirpath}/{device}.csv", usecols=col_list)
            df_measured1.columns = [
                f"{vds}{int(i/2)}",
                f"vgs ={vgs[0]}{int(i/2)}",
                f"vgs ={vgs[1]}{int(i/2)}",
                f"vgs ={vgs[2]}{int(i/2)}",
                f"vgs ={vgs[3]}{int(i/2)}",
                f"vgs ={vgs[4]}{int(i/2)}",
                f"vgs ={vgs[5]}{int(i/2)}",
            ]
        all_dfs.append(df_measured)
        all_dfs1.append(df_measured1)

    dfs = pd.concat(all_dfs, axis=1)
    dfs1 = pd.concat(all_dfs1, axis=1)
    dfs.drop_duplicates(inplace=True)
    dfs1.drop_duplicates(inplace=True)
    return dfs, dfs1


def run_sim(
    dirpath: str, device: str, id_rds: str, width: float, length: float, temp=25
) -> dict:
    """Run simulation at specific information and corner
    Args:
        dirpath(str): path to the file where we write data
        device(str): the device instance will be simulated
        id_rds(str): select id or rds
        temp(float): a specific temp for simulation
        width(float): a specific width for simulation
        length(float): a specific length for simulation

    Returns:
        info(dict): results are stored in,
        and passed to the run_sims function to extract data
    """
    netlist_tmp = f"device_netlists_{id_rds}/{device}.spice"

    info = {}
    info["device"] = device
    info["temp"] = temp
    info["length"] = length
    info["width"] = width

    width_str = width
    length_str = length
    temp_str = temp

    s = f"netlist_w{width_str}_l{length_str}_t{temp_str}.spice"
    netlist_path = f"{dirpath}/{device}_netlists_{id_rds}/{s}"
    s = f"t{temp}_simulated_W{width_str}_L{length_str}.csv"
    result_path = f"{dirpath}/simulated_{id_rds}/{s}"
    os.makedirs(f"{dirpath}/simulated_{id_rds}", exist_ok=True)

    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        os.makedirs(f"{dirpath}/{device}_netlists_{id_rds}", exist_ok=True)
        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device,
                    width=width_str,
                    length=length_str,
                    temp=temp_str,
                    AD=float(width_str) * 0.24,
                    PD=2 * (float(width_str) + 0.24),
                    AS=float(width_str) * 0.24,
                    PS=2 * (float(width_str) + 0.24),
                )
            )

    # Running ngspice for each netlist
    try:
        call_simulator(netlist_path)

        if os.path.exists(result_path):
            mos_iv = result_path
        else:
            mos_iv = "None"

    except Exception:
        mos_iv = "None"

    info["mos_iv_simulated"] = mos_iv

    return info


def run_sims(
    df: pd.DataFrame, dirpath: str, device: str, id_rds: str, num_workers=mp.cpu_count()
) -> pd.DataFrame:
    """passing netlists to run_sim function
        and storing the results csv files into dataframes

    Args:
        df(pd.DataFrame): dataframe passed from the ext_measured function
        dirpath(str): the path to the file where we write data
        device(str): name of the device
        id_rds(str): select id or rds
        num_workers=mp.cpu_count() (int): num of cpu used
    Returns:
        df(pd.DataFrame): dataframe contains simulated results
    """
    loops = df["L (um)"].count()
    temp_range = int(loops / 3)
    df["temp"] = 25
    df["temp"][temp_range : 2 * temp_range] = -40
    df["temp"][2 * temp_range : 3 * temp_range] = 125

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures_list = []
        for j, row in df.iterrows():
            futures_list.append(
                executor.submit(
                    run_sim,
                    dirpath,
                    device,
                    id_rds,
                    row["W (um)"],
                    row["L (um)"],
                    row["temp"],
                )
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logging.info("Test case generated an exception: %s" % (exc))

    sf = glob.glob(f"{dirpath}/simulated_{id_rds}/*.csv")

    # sweeping on all generated cvs files
    for i in range(len(sf)):
        sdf = pd.read_csv(
            sf[i],
            header=None,
            delimiter=r"\s+",
        )
        sweep = int(sdf[0].count() / len(NMOS3P3_VGS))
        new_array = np.empty((sweep, 1 + int(sdf.shape[0] / sweep)))

        new_array[:, 0] = sdf.iloc[1 : sweep + 1, 0]
        times = int(sdf.shape[0] / sweep)

        for j in range(times):
            new_array[:, (j + 1)] = sdf.iloc[j * sweep + 1 : (j + 1) * sweep + 1, 0]

        # Writing final simulated data 1
        sdf = pd.DataFrame(new_array)
        sdf.rename(
            columns={
                0: "vds",
                1: "vb1",
                2: "vb2",
                3: "vb3",
                4: "vb4",
                5: "vb5",
                6: "vb6",
            },
            inplace=True,
        )
        sdf.to_csv(sf[i], index=False)

    df = pd.DataFrame(results)
    return df


def error_cal(
    df: pd.DataFrame,
    sim_df: pd.DataFrame,
    meas_df: pd.DataFrame,
    dev_path: str,
    device: str,
    id_rds: str,
    vds: str,
    vgs: list[str],
) -> None:
    """error function calculates the error between measured, simulated data

    Args:
        df(pd.DataFrame): Dataframe contains devices and csv files
          which represent measured, simulated data
        sim_df(pd.DataFrame): Dataframe contains devices and csv files simulated
        meas_df(pd.DataFrame): Dataframe contains devices and csv files measured
        dev_path(str): The path in which we write data
        id_rds(str): select id or rds

    """
    # adding error columns to the merged dataframe
    merged_dfs = list()
    loops = df["L (um)"].count()
    temp_range = int(loops / 3)
    df["temp"] = 25
    df["temp"][temp_range : 2 * temp_range] = -40
    df["temp"][2 * temp_range : 3 * temp_range] = 125

    for i in range(len(sim_df)):
        length = df["L (um)"].iloc[int(i)]
        w = df["W (um)"].iloc[int(i)]
        t = df["temp"].iloc[int(i)]
        s = f"t{t}_simulated_W{w}_L{length}.csv"
        sim_path = f"mos_iv_reg/{device}/simulated_{id_rds}/{s}"

        simulated_data = pd.read_csv(sim_path)

        measured_data = meas_df[
            [
                f"{vds}0",
                f"vgs ={vgs[0]}{i}",
                f"vgs ={vgs[1]}{i}",
                f"vgs ={vgs[2]}{i}",
                f"vgs ={vgs[3]}{i}",
                f"vgs ={vgs[4]}{i}",
                f"vgs ={vgs[5]}{i}",
            ]
        ].copy()
        measured_data.rename(
            columns={
                f"{vds}0": "vds",
                f"vgs ={vgs[0]}{i}": "measured_vgs1",
                f"vgs ={vgs[1]}{i}": "measured_vgs2",
                f"vgs ={vgs[2]}{i}": "measured_vgs3",
                f"vgs ={vgs[3]}{i}": "measured_vgs4",
                f"vgs ={vgs[4]}{i}": "measured_vgs5",
                f"vgs ={vgs[5]}{i}": "measured_vgs6",
            },
            inplace=True,
        )
        measured_data.dropna(inplace=True)
        simulated_data["vds"] = measured_data["vds"]

        result_data = simulated_data.merge(measured_data, how="left")
        result_data.loc[0] = 1

        result_data["step1_error"] = (
            np.abs(result_data["measured_vgs1"] - result_data["vb1"])
            * 100.0
            / (result_data["measured_vgs1"])
        )
        result_data["step2_error"] = (
            np.abs(result_data["measured_vgs2"] - result_data["vb2"])
            * 100.0
            / (result_data["measured_vgs2"])
        )
        result_data["step3_error"] = (
            np.abs(result_data["measured_vgs3"] - result_data["vb3"])
            * 100.0
            / (result_data["measured_vgs3"])
        )
        result_data["step4_error"] = (
            np.abs(result_data["measured_vgs4"] - result_data["vb4"])
            * 100.0
            / (result_data["measured_vgs4"])
        )
        result_data["step5_error"] = (
            np.abs(result_data["measured_vgs5"] - result_data["vb5"])
            * 100.0
            / (result_data["measured_vgs5"])
        )
        result_data["step6_error"] = (
            np.abs(result_data["measured_vgs6"] - result_data["vb6"])
            * 100.0
            / (result_data["measured_vgs6"])
        )
        result_data["error"] = (
            np.abs(
                result_data["step1_error"]
                + result_data["step2_error"]
                + result_data["step3_error"]
                + result_data["step4_error"]
                + result_data["step5_error"]
                + result_data["step6_error"]
            )
            / 6
        )

        merged_dfs.append(result_data)
        merged_out = pd.concat(merged_dfs)
        merged_out.fillna(0, inplace=True)
        merged_out.to_csv(f"{dev_path}/error_analysis_{id_rds}.csv", index=False)
    return None


def main():
    """Main function applies all regression steps"""
    # ======= Checking Xyce  =======
    Xyce_v_ = os.popen("Xyce  -v 2> /dev/null").read()
    if Xyce_v_ == "":
        logging.error("Xyce is not found. Please make sure Xyce is installed.")
        exit(1)
    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    devices = [
        "nfet_03v3_iv",
        "pfet_03v3_iv",
        "nfet_06v0_iv",
        "pfet_06v0_iv",
        "nfet_06v0_nvt_iv",
        "nfet_03v3_dss_iv",
        "pfet_03v3_dss_iv",
        "nfet_06v0_dss_iv",
        "pfet_06v0_dss_iv",
    ]
    nmos_vds = "vds (V)"
    pmos_vds = "-vds (V)"
    Id_sim = "Id"
    Rds_sim = "Rds"

    for device in devices:
        # Folder structure of measured values
        dirpath = f"mos_iv_reg/{device}"
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
        os.makedirs(f"{dirpath}", exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {device}")

        # Folder structure of simulated values
        os.makedirs(f"{dirpath}/simulated_{Id_sim}", exist_ok=False)
        os.makedirs(f"{dirpath}/simulated_{Rds_sim}", exist_ok=False)

        vds = nmos_vds
        if device[0] == "p":
            vds = pmos_vds

        vgs = NMOS3P3_VGS
        if device == "pfet_03v3_iv" or device == "pfet_03v3_dss_iv":
            vgs = PMOS3P3_VGS
        elif device == "pfet_06v0_iv" or device == "pfet_06v0_dss_iv":
            vgs = PMOS6P0_VGS
        elif device == "nfet_06v0_iv" or device == "nfet_06v0_dss_iv":
            vgs = NMOS6P0_VGS
        elif device == "nfet_06v0_nvt_iv":
            vgs = NMOS6P0_NAT_VGS
        data_files = glob.glob(f"../../180MCU_SPICE_DATA/MOS/{device}.nl_out.xlsx")
        if len(data_files) < 1:
            logging.info(f"# Can't find file for device: {device}")
            file = ""
        else:
            file = os.path.abspath(data_files[0])

        logging.info(f"#  data points file : {file}")

        if file != "":
            # From xlsx to csv
            read_file = pd.read_excel(
                f"../../180MCU_SPICE_DATA/MOS/{device}.nl_out.xlsx"
            )
            read_file.to_csv(f"{dirpath}/{device}.csv", index=False, header=True)
            meas_df, meas_df1 = ext_measured(dirpath, device, vds, vgs)
        else:
            meas_df = []

        df1 = pd.read_csv(f"{dirpath}/{device}.csv")
        df = df1[["L (um)", "W (um)"]].copy()
        df.dropna(inplace=True)
        sim_df_id = run_sims(df, dirpath, device, Id_sim)
        sim_df_rds = run_sims(df, dirpath, device, Rds_sim)

        logging.info(
            f"# Device {device} number of measured_datapoints for Id : {len(sim_df_id) * len(meas_df)}"
        )

        logging.info(
            f"# Device {device} number of simulated datapoints for Id : {len(sim_df_id) * len(meas_df)} "
        )

        logging.info(
            f"# Device {device} number of measured_datapoints for Rds : {len(sim_df_rds) * len(meas_df1)}"
        )
        logging.info(
            f"# Device {device} number of simulated datapoints for Rds : {len(sim_df_rds) * len(meas_df1)}"
        )

        # passing dataframe to the error_calculation function
        # calling error function for creating statistical csv file

        error_cal(df, sim_df_id, meas_df, dirpath, device, Id_sim, vds, vgs)
        error_cal(df, sim_df_id, meas_df1, dirpath, device, Rds_sim, vds, vgs)

        # reading from the csv file contains all error data
        # merged_all contains all simulated, measured, error data
        for s in ["Id", "Rds"]:
            merged_all = pd.read_csv(f"{dirpath}/error_analysis_{s}.csv")

            # calculating the error of each device and reporting it
            min_error_total = float()
            max_error_total = float()
            error_total = float()

            # number of rows in the final excel sheet
            num_rows = merged_all["error"].count()

            for n in range(num_rows):
                error_total += merged_all["error"][n]
                if merged_all["error"][n] > max_error_total:
                    max_error_total = merged_all["error"][n]
                elif merged_all["error"][n] < min_error_total:
                    min_error_total = merged_all["error"][n]

            mean_error_total = error_total / num_rows

            # Making sure that min, max, mean errors are not > 100%
            if min_error_total > 100:
                min_error_total = 100

            if max_error_total > 100:
                max_error_total = 100

            if mean_error_total > 100:
                mean_error_total = 100

            # logging.infoing min, max, mean errors to the consol
            logging.info(
                f"# Device {device} {s} min error: {min_error_total:.2f}, max error: {max_error_total:.2f}, mean error {mean_error_total:.2f}"
            )

            if max_error_total < PASS_THRESH:
                logging.info(f"# Device {device} {s} has passed regression.")
            else:
                logging.error(f"# Device {device} {s} has failed regression.")


# # ================================================================
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
