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
NMOS3P3_VBS = [0, -0.825, -1.65, -2.48, -3.3]
PMOS3P3_VBS = [0, 0.825, 1.65, 2.48, 3.3]
NMOS6P0_VBS = [0, -0.75, -1.5, -2.25, -3]
PMOS6P0_VBS = [0, 0.75, 1.5, 2.25, 3]
NMOS6P0_NAT_VBS = [0, -0.75, -1.5, -2.25, -3]
NMOS3P3_VBS1 = [0, -0.825, -1.65, -2.475, -3.3]
PMOS3P3_VBS1 = [0, 0.825, 1.65, 2.475, 3.3]
PASS_THRESH = 2.0

# ################
VBS_N03V3 = "0 -3.3 -0.825"
VBS_P03V3 = "0 3.3 0.825"
VBS_N06V0 = "0 -3 -0.75"
VBS_P06V0 = "0 3 0.75"
VBS_N06V0_N = "0 -3 -0.75"

VGS_N03V3 = "0 3.3 0.05"
VGS_P03V3 = "0 -3.3 -0.05"
VGS_N06V0 = "0 6 0.05"
VGS_P06V0 = "0 -6 -0.05"
VGS_N06V0_N = "-0.5 6 0.05"


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    log_file = file_name.replace("-hspice-ext all ", "")
    os.system(f"Xyce {file_name} -l {log_file}.log 2> /dev/null")


def ext_measured(dirpath: str, device: str, vgs: str, vbs: list[str]) -> pd.DataFrame:
    """ext_measured function calculates get measured data

    Args:
        dirpath(str): measured data path
        device(str): npn or pnp
        vbs(list[str]): headers of rest column in the table
        vgs(str): header of first column in the table
    Returns:
        df(DataFrame): output measured df
    """

    # Get dimensions used for each device
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv", usecols=["W (um)", "L (um)"])
    loops = dimensions["L (um)"].count()
    all_dfs = []

    # Extracting measured values for each W & L
    for i in range(0, loops * 2, 2):

        # Special case for 1st measured values
        if i == 0:
            # measured Id
            if device[0] == "p":
                col_list = [
                    "-vgs ",
                    f"vbs ={vbs[0]}",
                    f"vbs ={vbs[1]}",
                    f"vbs ={vbs[2]}",
                    f"vbs ={vbs[3]}",
                    f"vbs ={vbs[4]}",
                ]
            else:
                col_list = [
                    "vgs ",
                    f"vbs ={vbs[0]}",
                    f"vbs ={vbs[1]}",
                    f"vbs ={vbs[2]}",
                    f"vbs ={vbs[3]}",
                    f"vbs ={vbs[4]}",
                ]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv", usecols=col_list)
            df_measured.columns = [
                f"{vgs}.0",
                f"vbs ={vbs[0]}.0",
                f"vbs ={vbs[1]}.0",
                f"vbs ={vbs[2]}.0",
                f"vbs ={vbs[3]}.0",
                f"vbs ={vbs[4]}.0",
            ]

        else:
            # measured Id
            col_list = [
                f"{vgs}.{i}",
                f"vbs ={vbs[0]}.{i}",
                f"vbs ={vbs[1]}.{i}",
                f"vbs ={vbs[2]}.{i}",
                f"vbs ={vbs[3]}.{i}",
                f"vbs ={vbs[4]}.{i}",
            ]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv", usecols=col_list)
            # measured Id
            df_measured.columns = [
                f"{vgs}.{int(i/2)}",
                f"vbs ={vbs[0]}.{int(i/2)}",
                f"vbs ={vbs[1]}.{int(i/2)}",
                f"vbs ={vbs[2]}.{int(i/2)}",
                f"vbs ={vbs[3]}.{int(i/2)}",
                f"vbs ={vbs[4]}.{int(i/2)}",
            ]
        all_dfs.append(df_measured)

    dfs = pd.concat(all_dfs, axis=1)
    dfs.drop_duplicates(inplace=True)
    return dfs


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
    if device[0] == "n":
        device1 = "nmos"
    else:
        device1 = "pmos"

    vbs = VBS_N03V3
    vgs = VGS_N03V3
    if device == "pfet_03v3" or device == "pfet_03v3_dss":
        vgs = VGS_P03V3
        vbs = VBS_P03V3
    elif device == "pfet_06v0" or device == "pfet_06v0_dss":
        vgs = VGS_P06V0
        vbs = VBS_P06V0
    elif device == "nfet_06v0" or device == "nfet_06v0_dss":
        vgs = VGS_N06V0
        vbs = VBS_N06V0
    elif device == "nfet_06v0_nvt":
        vgs = VGS_N06V0_N
        vbs = VBS_N06V0_N

    netlist_tmp = f"device_netlists_{id_rds}/{device1}.spice"

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
    result_path = f"{dirpath}/{device}_netlists_{id_rds}/{s}"

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
                    vgs=vgs,
                    vbs=vbs,
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
        Id_sim(str): select id
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

    sf = glob.glob(f"{dirpath}/{device}_netlists_{id_rds}/*.csv")
    if device == "pfet_03v3" or device == "pfet_03v3_dss":
        mos = PMOS3P3_VBS1
    elif device == "pfet_06v0" or device == "pfet_06v0_dss":
        mos = PMOS6P0_VBS
    elif (
        device == "nfet_06v0" or device == "nfet_06v0_nvt" or device == "nfet_06v0_dss"
    ):
        mos = NMOS6P0_VBS
    else:
        mos = NMOS3P3_VBS1
    # sweeping on all generated cvs files
    for i in range(len(sf)):
        df = pd.read_csv(sf[i])
        i_vds = "{-I(VDS)}"
        if device[0] == "p":
            i_vds = "{I(VDS)}"
        sdf = df.pivot(index="V(G_TN)", columns=("V(B_TN)"), values=i_vds)
        sdf.rename(
            columns={
                mos[0]: "simulated_vbs1",
                mos[1]: "simulated_vbs2",
                mos[2]: "simulated_vbs3",
                mos[3]: "simulated_vbs4",
                mos[4]: "simulated_vbs5",
            },
            inplace=True,
        )
        if device[0] == "p":
            # reverse the rows
            sdf = sdf.iloc[::-1]
        sdf.to_csv(sf[i], index=True, header=True, sep=",")

    df = pd.DataFrame(results)
    return df


def error_cal(
    df: pd.DataFrame,
    sim_df: pd.DataFrame,
    meas_df: pd.DataFrame,
    dev_path: str,
    device: str,
    id_rds: str,
    vbs: str,
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
    # create a new dataframe for rms error
    rms_df = pd.DataFrame(columns=["length", "width", "temp", "rms_error"])

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
        sim_path = f"mos_iv_reg/{device}/{device}_netlists_{id_rds}/{s}"

        simulated_data = pd.read_csv(sim_path)

        measured_data = meas_df[
            [
                f"{vgs}.0",
                f"vbs ={vbs[0]}.{i}",
                f"vbs ={vbs[1]}.{i}",
                f"vbs ={vbs[2]}.{i}",
                f"vbs ={vbs[3]}.{i}",
                f"vbs ={vbs[4]}.{i}",
            ]
        ].copy()
        measured_data.rename(
            columns={
                f"{vgs}.0": "vgs",
                f"vbs ={vbs[0]}.{i}": "measured_vbs1",
                f"vbs ={vbs[1]}.{i}": "measured_vbs2",
                f"vbs ={vbs[2]}.{i}": "measured_vbs3",
                f"vbs ={vbs[3]}.{i}": "measured_vbs4",
                f"vbs ={vbs[4]}.{i}": "measured_vbs5",
            },
            inplace=True,
        )
        measured_data.dropna(inplace=True)
        simulated_data["vgs"] = measured_data["vgs"]

        result_data = simulated_data.merge(measured_data, how="left")
        # clipping all the  values to lowest_curr
        lowest_curr = 5e-12
        result_data["measured_vbs1"] = result_data["measured_vbs1"].clip(
            lower=lowest_curr
        )
        result_data["measured_vbs2"] = result_data["measured_vbs2"].clip(
            lower=lowest_curr
        )
        result_data["measured_vbs3"] = result_data["measured_vbs3"].clip(
            lower=lowest_curr
        )
        result_data["measured_vbs4"] = result_data["measured_vbs4"].clip(
            lower=lowest_curr
        )
        result_data["measured_vbs5"] = result_data["measured_vbs5"].clip(
            lower=lowest_curr
        )
        result_data["simulated_vbs1"] = result_data["simulated_vbs1"].clip(lower=lowest_curr)
        result_data["simulated_vbs2"] = result_data["simulated_vbs2"].clip(lower=lowest_curr)
        result_data["simulated_vbs3"] = result_data["simulated_vbs3"].clip(lower=lowest_curr)
        result_data["simulated_vbs4"] = result_data["simulated_vbs4"].clip(lower=lowest_curr)
        result_data["simulated_vbs5"] = result_data["simulated_vbs5"].clip(lower=lowest_curr)

        result_data["step1_error"] = (
            np.abs(result_data["measured_vbs1"] - result_data["simulated_vbs1"])
            * 100.0
            / (result_data["measured_vbs1"])
        )
        result_data["step2_error"] = (
            np.abs(result_data["measured_vbs2"] - result_data["simulated_vbs2"])
            * 100.0
            / (result_data["measured_vbs2"])
        )
        result_data["step3_error"] = (
            np.abs(result_data["measured_vbs3"] - result_data["simulated_vbs3"])
            * 100.0
            / (result_data["measured_vbs3"])
        )
        result_data["step4_error"] = (
            np.abs(result_data["measured_vbs4"] - result_data["simulated_vbs4"])
            * 100.0
            / (result_data["measured_vbs4"])
        )
        result_data["step5_error"] = (
            np.abs(result_data["measured_vbs5"] - result_data["simulated_vbs5"])
            * 100.0
            / (result_data["measured_vbs5"])
        )

        result_data["error"] = (
            np.abs(
                result_data["step1_error"]
                + result_data["step2_error"]
                + result_data["step3_error"]
                + result_data["step4_error"]
                + result_data["step5_error"]
            )
            / 5
        )
        # get rms error
        result_data["rms_error"] = np.sqrt(np.mean(result_data["error"] ** 2))
        # fill rms dataframe
        rms_df.loc[i] = [
            length,
            w,
            t,
            result_data["rms_error"].iloc[0],
        ]

        merged_dfs.append(result_data)
    merged_out = pd.concat(merged_dfs)
    merged_out.fillna(0, inplace=True)
    merged_out.to_csv(f"{dev_path}/error_analysis_{id_rds}.csv", index=False)
    rms_df.to_csv(f"{dev_path}/final_error_analysis_{id_rds}.csv", index=False)
    return None


def main():
    """Main function applies all regression steps"""
        # ======= Checking Xyce  =======
    Xyce_v_ = os.popen("Xyce  -v 2> /dev/null").read()
    if Xyce_v_ == "":
        logging.error("Xyce is not found. Please make sure Xyce is installed.")
        exit(1)
    elif "7.6" not in Xyce_v_:
        logging.error("Xyce version 7.6 is required.")
        exit(1)
    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

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
    ]  # "nfet_03v3_dss"
    nmos_vgs = "vgs (V)"
    pmos_vgs = "-vgs (V)"
    Id_sim = "Id"

    for device in devices:
        # Folder structure of measured values
        dirpath = f"mos_iv_reg/{device}"
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
        os.makedirs(f"{dirpath}", exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {device}")

        vgs = nmos_vgs
        if device[0] == "p":
            vgs = pmos_vgs

        vbs = NMOS3P3_VBS
        if device == "pfet_03v3" or device == "pfet_03v3_dss":
            vbs = PMOS3P3_VBS
        elif device == "pfet_06v0" or device == "pfet_06v0_dss":
            vbs = PMOS6P0_VBS
        elif device == "nfet_06v0" or device == "nfet_06v0_dss":
            vbs = NMOS6P0_VBS
        elif device == "nfet_06v0_nvt":
            vbs = NMOS6P0_NAT_VBS
        data_files = glob.glob(f"../../180MCU_SPICE_DATA/MOS/{device}_iv.nl_out.xlsx")
        if len(data_files) < 1:
            logging.info(f"# Can't find file for device: {device}")
            file = ""
        else:
            file = os.path.abspath(data_files[0])

        logging.info(f"#  data points file : {file}")

        if file != "":
            # From xlsx to csv
            read_file = pd.read_excel(
                f"../../180MCU_SPICE_DATA/MOS/{device}_iv.nl_out.xlsx"
            )
            read_file.to_csv(f"{dirpath}/{device}.csv", index=False, header=True)
            meas_df = ext_measured(dirpath, device, vgs, vbs)

        else:
            meas_df = []

        df1 = pd.read_csv(f"{dirpath}/{device}.csv")
        df = df1[["L (um)", "W (um)"]].copy()
        df.dropna(inplace=True)
        sim_df = run_sims(df, dirpath, device, Id_sim)

        logging.info(
            f"# Device {device} number of measured_datapoints for Id : {len(sim_df) * len(meas_df)}"
        )

        logging.info(
            f"# Device {device} number of simulated datapoints for Id : {len(sim_df) * len(meas_df)} "
        )
        error_cal(df, sim_df, meas_df, dirpath, device, Id_sim, vbs, vgs)

        # reading from the csv file contains all error data
        # merged_all contains all simulated, measured, error data
        merged_all = pd.read_csv(f"{dirpath}/final_error_analysis_{Id_sim}.csv")

        # calculating the error of each device and reporting it
        min_error_total = float()
        max_error_total = float()
        mean_error_total = float()
        # number of rows in the final excel sheet

        min_error_total = merged_all["rms_error"].min()
        max_error_total = merged_all["rms_error"].max()
        mean_error_total = merged_all["rms_error"].mean()
        # Making sure that min, max, mean errors are not > 100%
        if min_error_total > 100:
            min_error_total = 100

        if max_error_total > 100:
            max_error_total = 100

        if mean_error_total > 100:
            mean_error_total = 100

        # logging.infoing min, max, mean errors to the consol
        logging.info(
            f"# Device {device} min error: {min_error_total:.2f}, max error: {max_error_total:.2f}, mean error {mean_error_total:.2f}"
        )

        if max_error_total < PASS_THRESH:
            logging.info(f"# Device {device} has passed regression.")
        else:
            logging.error(f"# Device {device} has failed regression.")


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
