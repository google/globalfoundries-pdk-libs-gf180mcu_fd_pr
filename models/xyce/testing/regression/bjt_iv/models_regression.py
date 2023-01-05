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

warnings.simplefilter(action="ignore", category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'
MOS=["ibp=1.000E-06", "ibp=3.000E-06", "ibp=5.000E-06", "ibp=7.000E-06", "ibp=9.000E-06"]
def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    os.system(f"Xyce -hspice-ext all {file_name} -l {file_name}.log")


def ext_measured(dirpath,device, vc, step, list_devices, ib):

    # Get dimensions used for each device
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv", usecols=["corners"])
    loops = dimensions["corners"].count()
    all_dfs = []

    # Extracting measured values for each Device
    for i in range(loops):
        k = i
        if i >= len(list_devices):
            while k >= len(list_devices):
                k = k - len(list_devices)

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


def run_sim(dirpath, device, list_devices, temp=25):
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
            netlist.write(
                tmpl.render(
                    device=list_devices_str,
                    temp=temp_str

                )
            )

    # Running ngspice for each netlist
    try:
        call_simulator(netlist_path)

        if os.path.exists(result_path):
            bjt_iv = result_path
        else:
            bjt_iv = "None"

    except Exception:
        mos_iv = "None"

    info["bjt_iv_simulated"] = bjt_iv

    return info


def run_sims( dirpath, list_devices,device, num_workers=mp.cpu_count()):
    """passing netlists to run_sim function
        and storing the results csv files into dataframes

    Args:
        df(pd.DataFrame): dataframe passed from the ext_measured function
        dirpath(str): the path to the file where we write data
        id_rds(str): select id or rds
        num_workers=mp.cpu_count() (int): num of cpu used
        device(str): name of the device
    Returns:
        df(pd.DataFrame): dataframe contains simulated results
    """
    df1 = pd.read_csv(f"{dirpath}/{device}.csv", usecols=["corners"])
    loops = (df1["corners"]).count()
    temp_range = int(loops / 4)
    df=pd.DataFrame()
    df["dev"]=df1["corners"].dropna()
    df["dev"][0:temp_range]=list_devices
    df["dev"][temp_range:2*temp_range]=list_devices
    df["dev"][2*temp_range:3*temp_range]=list_devices
    df["dev"][3*temp_range:4*temp_range]=list_devices
    df["temp"]=25
    df["temp"][temp_range :2 * temp_range]=-40
    df["temp"][2*temp_range :3 * temp_range]=125
    df["temp"][3*temp_range :]=-175


    results = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=num_workers
    ) as executor:
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
                print("Test case generated an exception: %s" % (exc))
    sf = glob.glob(f"{dirpath}/simulated/*.csv")
    # sweeping on all generated cvs files
    for i in range(len(sf)):
        sdf = pd.read_csv(
            sf[i],
            header=None,
            delimiter=r"\s+",
        )
        sweep = int(sdf[0].count() / len(MOS))
        new_array = np.empty((sweep, 1 + int(sdf.shape[0] / sweep)))

        new_array[:, 0] = sdf.iloc[1:sweep+1, 0]
        times = int(sdf.shape[0] / sweep)

        for j in range(times):
            new_array[:, (j + 1)] = sdf.iloc[(j * sweep)+1: ((j + 1) * sweep)+1 , 0]

        # Writing final simulated data 1
        sdf = pd.DataFrame(new_array)
        sdf.rename(
            columns={
                0: "ibp1",
                1: "ibp2",
                2: "ibp3",
                3: "ibp4",
                4: "ibp5"
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
) -> None:
    """error function calculates the error between measured, simulated data

    Args:
        df(pd.DataFrame): Dataframe contains devices and csv files
          which represent measured, simulated data
        sim_df(pd.DataFrame): Dataframe contains devices and csv files simulated
        meas_df(pd.DataFrame): Dataframe contains devices and csv files measured
        dev_path(str): The path in which we write data

    """
  


def main():

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
    Id_sim = "IcVc"
    sweep = [61, 31]
    step = ["1.000E-06", "3.000E-06", "5.000E-06", "7.000E-06", "9.000E-06"]

    for i, device in enumerate(devices):
        # Folder structure of measured values
        dirpath = f"mos_iv_reg/{device}"
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
        os.makedirs(f"{dirpath}", exist_ok=False)

        # From xlsx to csv
        read_file = pd.read_excel(
            f"../../180MCU_SPICE_DATA/BJT/bjt_{device}_icvc_f.nl_out.xlsx"
        )
        read_file.to_csv(f"{dirpath}/{device}.csv", index=False, header=True)

        # Folder structure of simulated values
        os.makedirs(f"{dirpath}/simulated", exist_ok=False)
        os.makedirs(f"{dirpath}/error_{Id_sim}", exist_ok=False)

        # =========== Simulate ==============
        df=ext_measured(dirpath,device, vc[i], step, list_devices[i], ib[i])
        
        run_sims( dirpath,list_devices[i], device, num_workers=mp.cpu_count())
        # ext_simulated(dirpath,device, vc[i], step, sweep[i], Id_sim, list_devices[i], ib[i])
        
        # ============ Results =============
        # error_cal(dirpath,device,df, vc[i], step, Id_sim, list_devices[i], ib[i])


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

    # Calling main function
    main()
