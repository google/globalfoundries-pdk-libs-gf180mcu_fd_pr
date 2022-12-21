# Copyright 2022 GlobalFoundries PDK Authors
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

  -h, --help             Show help text.
  -v, --version          Show version.
  --num_cores=<num>      Number of cores to be used by simulator
"""

from docopt import docopt
import pandas as pd
import numpy as np
import os
from jinja2 import Template
import concurrent.futures
import shutil
import multiprocessing as mp

import glob
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)
PASS_THRESH = 2.0


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name(str): Netlist file name.
    """
    return os.system(
        f"ngspice -b -a {file_name} -o {file_name}.log > {file_name}.log"
    )


def find_bjt(filepath):
    """check if bjt exists in csv files"""

    return os.path.exists(filepath)


def ext_npn_measured(icvc_file: str, devices: str, dev_path: str):
    """Extracting the measured data of npn devices from excel sheet

    Args:
         icvc_file(str): path to the data sheet
         devices(str): list for undertest devices
         dev_path(str): A path where extracted data is stored

    Returns:
         df_measured: A data frame contains all extracted data

    """

    # Reading excel sheet and creating data frame
    df = pd.read_excel(icvc_file)
    loops = df["corners"].count()
    temp_range = int(loops / 4)
    all_dfs = list()

    # Extracting measured values for each Device
    for i in range(loops):

        # building up temperature
        if i in range(0, temp_range):
            temp = 25
        elif i in range(temp_range, 2 * temp_range):
            temp = -40
        elif i in range(2 * temp_range, 3 * temp_range):
            temp = 125
        else:
            temp = 175

        tempr = list()
        dev = list()
        ib_meas = list()

        k = i
        if i >= len(devices):
            while k >= len(devices):
                k = k - len(devices)

        # Special case for 1st measured values
        if i == 0:

            idf_ib = df[
                [
                    "vcp ",
                    "ibp =1.000E-06",
                    "ibp =3.000E-06",
                    "ibp =5.000E-06",
                    "ibp =7.000E-06",
                    "ibp =9.000E-06",
                ]
            ].copy()

            idf_ib.rename(
                columns={
                    "vcp ": "measured_collector_volt",
                    "ibp =1.000E-06": "measured_ibp_step1",
                    "ibp =3.000E-06": "measured_ibp_step2",
                    "ibp =5.000E-06": "measured_ibp_step3",
                    "ibp =7.000E-06": "measured_ibp_step4",
                    "ibp =9.000E-06": "measured_ibp_step5",
                },
                inplace=True,
            )

        else:

            idf_ib = df[
                [
                    "vcp ",
                    f"ibp =1.000E-06.{i}",
                    f"ibp =3.000E-06.{i}",
                    f"ibp =5.000E-06.{i}",
                    f"ibp =7.000E-06.{i}",
                    f"ibp =9.000E-06.{i}",
                ]
            ].copy()

            idf_ib.rename(
                columns={
                    "vcp ": "measured_collector_volt",
                    f"ibp =1.000E-06.{i}": "measured_ibp_step1",
                    f"ibp =3.000E-06.{i}": "measured_ibp_step2",
                    f"ibp =5.000E-06.{i}": "measured_ibp_step3",
                    f"ibp =7.000E-06.{i}": "measured_ibp_step4",
                    f"ibp =9.000E-06.{i}": "measured_ibp_step5",
                },
                inplace=True,
            )

        os.makedirs(f"{dev_path}/ib_measured", exist_ok=True)
        idf_ib.to_csv(
            f"{dev_path}/ib_measured/measured_{devices[k]}_t{temp}.csv"
        )

        dev.append(devices[k])
        tempr.append(temp)
        ib_meas.append(
            f"{dev_path}/ib_measured/measured_{devices[k]}_t{temp}.csv"
        )

        sdf = {
            "device": dev,
            "temp": tempr,
            "ib_measured": ib_meas,
        }
        sdf = pd.DataFrame(sdf)
        all_dfs.append(sdf)

    df = pd.concat(all_dfs)
    df.dropna(axis=0, inplace=True)
    df = df[["device", "temp", "ib_measured"]]

    return df


def ext_pnp_measured(icvc_file: str, devices: str, dev_path: str):
    """Extracting the measured data of pnp devices from excel sheet

    Args:
         icvc_file(str): path to the data sheet
         devices(str): list for undertest devices
         dev_path(str): A path where extracted data is stored

    Returns:
         df_measured: A data frame contains all extracted data

    """

    # Reading excel sheet and creating data frame
    df = pd.read_excel(icvc_file)
    loops = df["corners"].count()
    temp_range = int(loops / 4)
    all_dfs = list()

    # Extracting measured values for each Device
    for i in range(loops):

        # building up temperature
        if i in range(0, temp_range):
            temp = 25
        elif i in range(temp_range, 2 * temp_range):
            temp = -40
        elif i in range(2 * temp_range, 3 * temp_range):
            temp = 125
        else:
            temp = 175

        tempr = list()
        dev = list()
        ib_meas = list()

        k = i
        if i >= len(devices):
            while k >= len(devices):
                k = k - len(devices)

        # Special case for 1st measured values
        if i == 0:

            idf_ib = df[
                [
                    "-vc ",
                    "ib =-1.000E-06",
                    "ib =-3.000E-06",
                    "ib =-5.000E-06",
                    "ib =-7.000E-06",
                    "ib =-9.000E-06",
                ]
            ].copy()

            idf_ib.rename(
                columns={
                    "-vc ": "measured_collector_volt",
                    "ib =-1.000E-06": "measured_ibp_step1",
                    "ib =-3.000E-06": "measured_ibp_step2",
                    "ib =-5.000E-06": "measured_ibp_step3",
                    "ib =-7.000E-06": "measured_ibp_step4",
                    "ib =-9.000E-06": "measured_ibp_step5",
                },
                inplace=True,
            )

        else:

            idf_ib = df[
                [
                    "-vc ",
                    f"ib =-1.000E-06.{i}",
                    f"ib =-3.000E-06.{i}",
                    f"ib =-5.000E-06.{i}",
                    f"ib =-7.000E-06.{i}",
                    f"ib =-9.000E-06.{i}",
                ]
            ].copy()

            idf_ib.rename(
                columns={
                    "-vc ": "measured_collector_volt",
                    f"ib =-1.000E-06.{i}": "measured_ibp_step1",
                    f"ib =-3.000E-06.{i}": "measured_ibp_step2",
                    f"ib =-5.000E-06.{i}": "measured_ibp_step3",
                    f"ib =-7.000E-06.{i}": "measured_ibp_step4",
                    f"ib =-9.000E-06.{i}": "measured_ibp_step5",
                },
                inplace=True,
            )

        os.makedirs(f"{dev_path}/ib_measured", exist_ok=True)
        idf_ib.to_csv(
            f"{dev_path}/ib_measured/measured_{devices[k]}_t{temp}.csv"
        )

        dev.append(devices[k])
        tempr.append(temp)
        ib_meas.append(
            f"{dev_path}/ib_measured/measured_{devices[k]}_t{temp}.csv"
        )

        sdf = {
            "device": dev,
            "temp": tempr,
            "ib_measured": ib_meas,
        }
        sdf = pd.DataFrame(sdf)
        all_dfs.append(sdf)

    df = pd.concat(all_dfs)
    df.dropna(axis=0, inplace=True)
    df = df[["device", "temp", "ib_measured"]]

    return df


def run_sim(dirpath, device, temp):
    """Run simulation at specific information and corner
    Args:
        dirpath(str): path to the file where we write data
        device(str): the device instance will be simulated
        temp: a specific temp for simulation

    Returns:
        info(dict): results are stored in
        and passed to the run_sims function to extract data
    """

    info = dict()
    info["device"] = device
    info["temp"] = temp
    dev = device.split("_")[0]

    netlist_tmp = f"./device_netlists/{dev}.spice"

    temp_str = "{:.1f}".format(temp)

    netlist_path = (
        f"{dirpath}/{dev}_netlists/netlist_{device}_t{temp_str}.spice"
    )

    result_path = f"{dirpath}/ib_simulated/simulated_{device}_t{temp_str}.csv"

    # initiating the directory in which results will be stored
    os.makedirs(f"{dirpath}/ib_simulated", exist_ok=True)

    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        os.makedirs(f"{dirpath}/{dev}_netlists", exist_ok=True)

        with open(netlist_path, "w") as netlist:
            netlist.write(
                tmpl.render(
                    device=device,
                    temp=temp_str,
                )
            )

    # Running ngspice for each netlist
    try:
        call_simulator(netlist_path)
        # Find bjt in csv
        if find_bjt(result_path):
            bjt_simu_ib = result_path
        else:
            bjt_simu_ib = "None"
    except Exception:
        bjt_simu_ib = "None"

    info["beta_sim_ib_unscaled"] = bjt_simu_ib

    return info


def run_sims(df, dirpath: str, num_workers=mp.cpu_count()):
    """passing netlists to run_sim function
        and storing the results csv files into dataframes

    Args:
        df: input dataframe passed from the ext_measured function
        dirpath(str): the path to the file where we write data
        num_workers=mp.cpu_count() (int): num of cpu used

    Returns:
        df: dataframe contains simulated results
    """

    results = list()
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=num_workers
    ) as executor:
        futures_list = list()
        for j, row in df.iterrows():
            futures_list.append(
                executor.submit(run_sim, dirpath, row["device"], row["temp"])
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                print("Test case generated an exception: %s" % (exc))

    sf = glob.glob(f"{dirpath}/ib_simulated/*.csv")

    # sweeping on all generated cvs files
    for i in range(len(sf)):
        sdf = pd.read_csv(
            sf[i],
            header=None,
            delimiter=r"\s+",
        )
        sweep = len(pd.read_csv(glob.glob(f"{dirpath}/ib_measured/*.csv")[1]))
        new_array = np.empty((sweep, 1 + int(sdf.shape[0] / sweep)))
        new_array[:, 0] = sdf.iloc[:sweep, 0]
        times = int(sdf.shape[0] / sweep)

        for j in range(times):
            new_array[:, (j + 1)] = sdf.iloc[j * sweep : (j + 1) * sweep, 1]

        # Writing final simulated data 1
        sdf = pd.DataFrame(new_array)
        sdf.to_csv(
            sf[i],
            index=False,
        )
        sdf.rename(
            columns={
                0: "simulated_collector_volt",
                1: "simulated_ibp_step1",
                2: "simulated_ibp_step2",
                3: "simulated_ibp_step3",
                4: "simulated_ibp_step4",
                5: "simulated_ibp_step3",
            },
            inplace=True,
        )
        sdf.to_csv(sf[i])
    df = pd.DataFrame(results)

    df = df[["device", "temp", "beta_sim_ib_unscaled"]]
    df["beta_ib_sim"] = df["beta_sim_ib_unscaled"]

    return df


def main():
    """Main function applies all regression steps"""

    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    main_regr_dir = "bjt_iv_regr"
    devices = ["npn", "pnp"]

    npn_devices = [
        "npn_10p00x10p00",
        "npn_05p00x05p00",
        "npn_00p54x16p00",
        "npn_00p54x08p00",
        "npn_00p54x04p00",
        "npn_00p54x02p00",
    ]

    pnp_devices = [
        "pnp_10p00x00p42",
        "pnp_05p00x00p42",
        "pnp_10p00x10p00",
        "pnp_05p00x05p00",
    ]

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(f"{dev_path}", exist_ok=False)

        print("######" * 10)
        print(f"# Checking Device {dev}")

        icvc_data_files = glob.glob(
            f"../../180MCU_SPICE_DATA/BJT/bjt_{dev}_icvc_f.nl_out.xlsx"
        )
        if len(icvc_data_files) < 1:
            print("# Can't find data file for device: {}".format(dev))
            icvc_file = ""
        else:
            icvc_file = icvc_data_files[0]
        print("# bjt_iv data points file : ", icvc_file)

        if icvc_file == "":
            print(f"# No datapoints available for validation for device {dev}")
            continue

        if dev == "npn":
            list_dev = npn_devices
            func = ext_npn_measured
        elif dev == "pnp":
            list_dev = pnp_devices
            func = ext_pnp_measured

        if icvc_file != "":
            meas_df = func(icvc_file, list_dev, dev_path)
        else:
            meas_df = list()

        meas_len = len(
            pd.read_csv(glob.glob(f"{dev_path}/ib_measured/*.csv")[1])
        )

        print(
            f"# Device {dev} number of measured_datapoints : ",
            len(meas_df) * meas_len,
        )

        #assuming number of used cores is 3 
        sim_df = run_sims(meas_df, dev_path, 3)
        print(sim_df)

        # Merging measured dataframe with the simulated one
        merged_df = meas_df.merge(sim_df, on=["device", "temp"], how="left")

        merged_all = list()     


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

    # Calling main function
    main()
