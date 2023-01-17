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
import multiprocessing as mp
import glob
import logging

PASS_THRESH = 2.0
warnings.simplefilter(action="ignore", category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'
MOS = [
    "ibp=1.000E-06",
    "ibp=3.000E-06",
    "ibp=5.000E-06",
    "ibp=7.000E-06",
    "ibp=9.000E-06",
]
NPN = [-0.000001, -0.000003, -0.000005, -0.000007, -0.000009]
PNP = [0.000001, 0.000003, 0.000005, 0.000007, 0.000009]


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    os.system(f"Xyce -hspice-ext all {file_name} -l {file_name}.log 2>/dev/null")


def ext_measured(
    dirpath: str,
    device: str,
    vc: str,
    step: list[str],
    list_devices: list[str],
    ib: str,
) -> pd.DataFrame:
    """ext_measured function calculates get measured data

    Args:
        dirpath(str): measured data path
        device(str): npn or pnp
        vc(str): header of first column in the table
        step(str): voltage step
        list_devices(list[str]): name of the devices
        ib(str): select ib for npn or pnp
    Returns:
        df(DataFrame): output df

    """
    # Get dimensions used for each device
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv", usecols=["corners"])
    loops = dimensions["corners"].count()
    all_dfs = []

    # Extracting measured values for each Device
    for i in range(loops):
        # Special case for 1st measured values
        if i == 0:
            if device == "pnp":
                temp_vc = vc
                vc = "-vc "
            # measured Id_sim
            col_list = [
                f"{vc}",
                f"{ib}{step[0]}",
                f"{ib}{step[1]}",
                f"{ib}{step[2]}",
                f"{ib}{step[3]}",
                f"{ib}{step[4]}",
            ]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv", usecols=col_list)
            df_measured.columns = [
                f"{vc}",
                f"{ib}{step[0]}",
                f"{ib}{step[1]}",
                f"{ib}{step[2]}",
                f"{ib}{step[3]}",
                f"{ib}{step[4]}",
            ]
        else:
            if device == "pnp":
                vc = temp_vc
            # measured Id_sim
            col_list = [
                f"{vc}",
                f"{ib}{step[0]}.{i}",
                f"{ib}{step[1]}.{i}",
                f"{ib}{step[2]}.{i}",
                f"{ib}{step[3]}.{i}",
                f"{ib}{step[4]}.{i}",
            ]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv", usecols=col_list)
            df_measured.columns = [
                f"{vc}",
                f"{ib}{step[0]}",
                f"{ib}{step[1]}",
                f"{ib}{step[2]}",
                f"{ib}{step[3]}",
                f"{ib}{step[4]}",
            ]
        all_dfs.append(df_measured)
    dfs = pd.concat(all_dfs, axis=1)
    dfs.drop_duplicates(inplace=True)
    return dfs


def run_sim(dirpath: str, device: str, list_devices: list[str], temp: float) -> dict:
    """Run simulation at specific information and corner
    Args:
        dirpath(str): path to the file where we write data
        device(str): the device instance will be simulated
        list_devices(list[str]): name of the devices
        temp(float): a specific temp for simulation

    Returns:
        info(dict): results are stored in,
        and passed to the run_sims function to extract data
    """
    netlist_tmp = f"device_netlists/{device}.spice"

    info = {}
    info["device"] = device
    info["temp"] = temp
    info["dev"] = list_devices

    temp_str = temp
    list_devices_str = list_devices

    s = f"{list_devices_str}netlist_t{temp_str}.spice"
    netlist_path = f"{dirpath}/{device}_netlists/{s}"
    s = f"t{temp}_simulated_{list_devices_str}.csv"
    result_path = f"{dirpath}/simulated/{s}"
    os.makedirs(f"{dirpath}/simulated", exist_ok=True)

    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        os.makedirs(f"{dirpath}/{device}_netlists", exist_ok=True)
        with open(netlist_path, "w") as netlist:
            netlist.write(tmpl.render(device=list_devices_str, temp=temp_str))

    # Running ngspice for each netlist
    try:
        call_simulator(netlist_path)

        if os.path.exists(result_path):
            bjt_iv = result_path
        else:
            bjt_iv = "None"

    except Exception:
        bjt_iv = "None"

    info["bjt_iv_simulated"] = bjt_iv

    return info


def run_sims(
    dirpath: str, list_devices: list[str], device: str, num_workers=mp.cpu_count()
):
    """passing netlists to run_sim function
        and storing the results csv files into dataframes

    Args:
        dirpath(str): the path to the file where we write data
        list_devices(list[str]): name of the devices
        device(str): name of the device
        num_workers=mp.cpu_count() (int): num of cpu used
    Returns:
        df(pd.DataFrame): dataframe contains simulated results
    """
    df1 = pd.read_csv(f"{dirpath}/{device}.csv", usecols=["corners"])
    loops = (df1["corners"]).count()
    temp_range = int(loops / 4)
    df = pd.DataFrame()
    df["dev"] = df1["corners"].dropna()
    df["dev"][0:temp_range] = list_devices
    df["dev"][temp_range : 2 * temp_range] = list_devices
    df["dev"][2 * temp_range : 3 * temp_range] = list_devices
    df["dev"][3 * temp_range : 4 * temp_range] = list_devices
    df["temp"] = 25
    df["temp"][temp_range : 2 * temp_range] = -40
    df["temp"][2 * temp_range : 3 * temp_range] = 125
    df["temp"][3 * temp_range :] = -175

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures_list = []
        for j, row in df.iterrows():
            futures_list.append(
                executor.submit(
                    run_sim,
                    dirpath,
                    device,
                    row["dev"],
                    row["temp"],
                )
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logging.info(f"Test case generated an exception: {exc}")
    sf = glob.glob(f"{dirpath}/simulated/*.csv")

    # sweeping on all generated cvs files
    for i in range(len(sf)):
        df2 = pd.read_csv(sf[i])
        if device == "npn":
            i_v = "{-I(VCP)}"
            sdf = df2.pivot(index="V(C)", columns="I(VBP)", values=i_v)
            sdf.rename(
                columns={
                    NPN[0]: "ibp1",
                    NPN[1]: "ibp2",
                    NPN[2]: "ibp3",
                    NPN[3]: "ibp4",
                    NPN[4]: "ibp5",
                },
                inplace=True,
            )
        else:
            i_v = "{I(VCP)}"
            sdf = df2.pivot(index="V(C)", columns="I(VBP)", values=i_v)
            sdf.rename(
                columns={
                    PNP[0]: "ibp1",
                    PNP[1]: "ibp2",
                    PNP[2]: "ibp3",
                    PNP[3]: "ibp4",
                    PNP[4]: "ibp5",
                },
                inplace=True,
            )
            # reverse the rows
            sdf = sdf.iloc[::-1]
        sdf.to_csv(sf[i], index=True, header=True, sep=",")

    df1 = pd.DataFrame(results)

    return df


def error_cal(
    sim_df: pd.DataFrame,
    meas_df: pd.DataFrame,
    device: str,
    step: list[str],
    ib: str,
    vc: str,
) -> pd.DataFrame:
    """error function calculates the error between measured, simulated data

    Args:

        sim_df(pd.DataFrame): Dataframe contains devices and csv files simulated
        meas_df(pd.DataFrame): Dataframe contains devices and csv files measured
        device(str): name of the device
        step(list[str]): voltage steps
        ib(str): select ib for npn or pnp
        vc(str): select vc for npn or pnp
    Returns:
        df(pd.DataFrame): dataframe contains error results
    """
    merged_dfs = list()
    # create a new dataframe for rms error
    rms_df = pd.DataFrame(columns=["device", "temp", "rms_error"])

    meas_df.to_csv(
        f"bjt_iv_reg/{device}/{device}_measured.csv", index=False, header=True
    )
    meas_df = pd.read_csv(f"bjt_iv_reg/{device}/{device}_measured.csv")
    for i in range(len(sim_df)):
        t = sim_df["temp"].iloc[i]
        dev = sim_df["dev"].iloc[i]
        sim_path = f"bjt_iv_reg/{device}/simulated/t{t}_simulated_{dev}.csv"

        simulated_data = pd.read_csv(sim_path)
        if i == 0:
            measured_data = meas_df[
                [
                    f"{ib}{step[0]}",
                    f"{ib}{step[1]}",
                    f"{ib}{step[2]}",
                    f"{ib}{step[3]}",
                    f"{ib}{step[4]}",
                ]
            ].copy()

            measured_data.rename(
                columns={
                    f"{ib}{step[0]}": "m_ibp1",
                    f"{ib}{step[1]}": "m_ibp2",
                    f"{ib}{step[2]}": "m_ibp3",
                    f"{ib}{step[3]}": "m_ibp4",
                    f"{ib}{step[4]}": "m_ibp5",
                },
                inplace=True,
            )
        else:
            measured_data = meas_df[
                [
                    f"{ib}{step[0]}.{i}",
                    f"{ib}{step[1]}.{i}",
                    f"{ib}{step[2]}.{i}",
                    f"{ib}{step[3]}.{i}",
                    f"{ib}{step[4]}.{i}",
                ]
            ].copy()

            measured_data.rename(
                columns={
                    f"{ib}{step[0]}.{i}": "m_ibp1",
                    f"{ib}{step[1]}.{i}": "m_ibp2",
                    f"{ib}{step[2]}.{i}": "m_ibp3",
                    f"{ib}{step[3]}.{i}": "m_ibp4",
                    f"{ib}{step[4]}.{i}": "m_ibp5",
                },
                inplace=True,
            )
        measured_data["vcp"] = meas_df[f"{vc}"]
        simulated_data["vcp"] = meas_df[f"{vc}"]
        simulated_data["device"] = sim_df["dev"].iloc[i]
        measured_data["device"] = sim_df["dev"].iloc[i]
        simulated_data["temp"] = sim_df["temp"].iloc[i]
        measured_data["temp"] = sim_df["temp"].iloc[i]
        result_data = simulated_data.merge(measured_data, how="left")

        result_data["ib_step1_error"] = (
            np.abs(result_data["ibp1"] - result_data["m_ibp1"])
            * 100.0
            / (result_data["m_ibp1"])
        )
        result_data["ib_step2_error"] = (
            np.abs(result_data["ibp2"] - result_data["m_ibp2"])
            * 100.0
            / (result_data["m_ibp2"])
        )
        result_data["ib_step3_error"] = (
            np.abs(result_data["ibp3"] - result_data["m_ibp3"])
            * 100.0
            / (result_data["m_ibp3"])
        )
        result_data["ib_step4_error"] = (
            np.abs(result_data["ibp4"] - result_data["m_ibp4"])
            * 100.0
            / (result_data["m_ibp4"])
        )
        result_data["ib_step5_error"] = (
            np.abs(result_data["ibp5"] - result_data["m_ibp5"])
            * 100.0
            / (result_data["m_ibp5"])
        )
        result_data["error"] = (
            np.abs(
                result_data["ib_step1_error"]
                + result_data["ib_step2_error"]
                + result_data["ib_step3_error"]
                + result_data["ib_step4_error"]
                + result_data["ib_step5_error"]
            )
            / 5
        )
        # get rms error
        result_data["rms_error"] = np.sqrt(np.mean(result_data["error"] ** 2))
        # fill rms dataframe
        rms_df.loc[i] = [
            result_data["device"].iloc[0],
            result_data["temp"].iloc[0],
            result_data["rms_error"].iloc[0],
        ]
        merged_dfs.append(result_data)
    merged_out = pd.concat(merged_dfs)
    merged_out.fillna(0, inplace=True)
    merged_out.to_csv(f"bjt_iv_reg/{device}/error_analysis.csv", index=False)
    rms_df.to_csv(f"bjt_iv_reg/{device}/final_error_analysis.csv", index=False)
    return rms_df


def main():
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

    devices = ["npn", "pnp"]
    list_devices = [
        [
            "npn_10p00x10p00",
            "npn_05p00x05p00",
            "npn_00p54x16p00",
            "npn_00p54x08p00",
            "npn_00p54x04p00",
            "npn_00p54x02p00",
        ],
        ["pnp_10p00x00p42", "pnp_05p00x00p42", "pnp_10p00x10p00", "pnp_05p00x05p00"],
    ]
    vc = ["vcp ", "-vc (A)"]
    ib = ["ibp =", "ib =-"]
    step = ["1.000E-06", "3.000E-06", "5.000E-06", "7.000E-06", "9.000E-06"]
    for i, device in enumerate(devices):
        # Folder structure of measured values
        dirpath = f"bjt_iv_reg/{device}"
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
        os.makedirs(f"{dirpath}", exist_ok=False)

        read_file = glob.glob(
            f"../../180MCU_SPICE_DATA/BJT/bjt_{device}_icvc_f.nl_out.xlsx"
        )
        if len(read_file) < 1:
            logging.info(f"# Can't find data file for device: {device}")
            read_fil = ""
        else:
            read_fil = os.path.abspath(read_file[0])
        logging.info(f"# bjt_iv data points file : {read_fil}")

        if read_fil == "":
            logging.info(
                f"# No datapoints available for validation for device {device}"
            )
            continue
        # From xlsx to csv
        read_file = pd.read_excel(
            f"../../180MCU_SPICE_DATA/BJT/bjt_{device}_icvc_f.nl_out.xlsx"
        )
        read_file.to_csv(f"{dirpath}/{device}.csv", index=False, header=True)

        # Folder structure of simulated values
        os.makedirs(f"{dirpath}/simulated", exist_ok=False)

        # =========== Simulate ==============
        df = ext_measured(dirpath, device, vc[i], step, list_devices[i], ib[i])

        sims = run_sims(dirpath, list_devices[i], device, num_workers=mp.cpu_count())
        # ============ Results =============
        merged_all = error_cal(sims, df, device, step, ib[i], vc[i])

        for dev in list_devices[i]:
            min_error_total = float()
            max_error_total = float()
            error_total = float()
            number_of_existance = int()

            # number of rows in the final excel sheet
            num_rows = merged_all["device"].count()

            for n in range(num_rows):
                if dev == merged_all["device"].iloc[n]:
                    number_of_existance += 1
                    error_total += merged_all["rms_error"].iloc[n]
                    if merged_all["rms_error"].iloc[n] > max_error_total:
                        max_error_total = merged_all["rms_error"].iloc[n]
                    elif merged_all["rms_error"].iloc[n] < min_error_total:
                        min_error_total = merged_all["rms_error"].iloc[n]

            mean_error_total = error_total / number_of_existance

            # Making sure that min, max, mean errors are not > 100%
            if min_error_total > 100:
                min_error_total = 100

            if max_error_total > 100:
                max_error_total = 100

            if mean_error_total > 100:
                mean_error_total = 100

            # logging.infoing min, max, mean errors to the consol
            logging.info(
                f"# Device {dev} min error: {min_error_total:.2f}, max error: {max_error_total:.2f}, mean error {mean_error_total:.2f}"
            )

            if max_error_total < PASS_THRESH:
                logging.info(f"# Device {dev} has passed regression.")
            else:
                logging.error(
                    f"# Device {dev} has failed regression. Needs more analysis."
                )


# ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================

if __name__ == "__main__":

    # Args
    arguments = docopt(__doc__, version="comparator: 0.1")
    workers_count = (
        os.cpu_count() * 2
        if arguments["--num_cores"] == None
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
