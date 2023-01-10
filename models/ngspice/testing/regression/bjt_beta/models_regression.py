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
import logging
import glob

import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

PASS_THRESH = 2.0


def find_bjt(filepath):
    """
    Find bjt in csv files
    """
    return os.path.exists(filepath)


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    return os.system(f"ngspice -b -a {file_name} -o {file_name}.log > {file_name}.log")


def ext_npn_measured(dev_data_path, device, devices, dev_path):
    # Read Data
    df = pd.read_excel(dev_data_path)

    all_dfs = []

    loops = df["corners"].count()

    for i in range(loops):

        temp_range = int(loops / 4)
        if i in range(0, temp_range):
            temp = 25
        elif i in range(temp_range, 2 * temp_range):
            temp = -40
        elif i in range(2 * temp_range, 3 * temp_range):
            temp = 125
        else:
            temp = 175

        tempr = []
        dev = []
        ic_meas = []
        ib_meas = []

        k = i
        if i >= len(devices):
            while k >= len(devices):
                k = k - len(devices)

        # Special case for 1st measured values

        if i == 0:

            idf_ic = df[["vbp ", "vcp =1", "vcp =2", "vcp =3"]].copy()
            idf_ic.rename(
                columns={
                    "vbp ": "measured_base_volt",
                    "vcp =1": "measured_ic_vcp_step1",
                    "vcp =2": "measured_ic_vcp_step2",
                    "vcp =3": "measured_ic_vcp_step3",
                },
                inplace=True,
            )

        else:

            idf_ic = df[
                ["vbp ", f"vcp =1.{2*i}", f"vcp =2.{2*i}", f"vcp =3.{2*i}"]
            ].copy()
            idf_ic.rename(
                columns={
                    "vbp ": "measured_base_volt",
                    f"vcp =1.{2*i}": "measured_ic_vcp_step1",
                    f"vcp =2.{2*i}": "measured_ic_vcp_step2",
                    f"vcp =3.{2*i}": "measured_ic_vcp_step3",
                },
                inplace=True,
            )

        os.makedirs(f"{dev_path}/ic_measured", exist_ok=True)
        idf_ic.to_csv(f"{dev_path}/ic_measured/measured_{devices[k]}_t{temp}.csv")

        idf_ib = df[
            ["vbp ", f"vcp =1.{2*i+1}", f"vcp =2.{2*i+1}", f"vcp =3.{2*i+1}"]
        ].copy()
        idf_ib.rename(
            columns={
                "vbp ": "measured_base_volt",
                f"vcp =1.{2*i+1}": "measured_ib_vcp_step1",
                f"vcp =2.{2*i+1}": "measured_ib_vcp_step2",
                f"vcp =3.{2*i+1}": "measured_ib_vcp_step3",
            },
            inplace=True,
        )

        os.makedirs(f"{dev_path}/ib_measured", exist_ok=True)
        idf_ib.to_csv(f"{dev_path}/ib_measured/measured_{devices[k]}_t{temp}.csv")

        dev.append(devices[k])
        tempr.append(temp)
        ic_meas.append(f"{dev_path}/ic_measured/measured_{devices[k]}_t{temp}.csv")
        ib_meas.append(f"{dev_path}/ib_measured/measured_{devices[k]}_t{temp}.csv")

        sdf = {
            "device": dev,
            "temp": tempr,
            "ic_measured": ic_meas,
            "ib_measured": ib_meas,
        }
        sdf = pd.DataFrame(sdf)
        all_dfs.append(sdf)

    df = pd.concat(all_dfs)
    df.dropna(axis=0, inplace=True)
    df["corner"] = "typical"
    df = df[["device", "temp", "corner", "ic_measured", "ib_measured"]]

    return df


def ext_pnp_measured(dev_data_path, device, devices, dev_path):
    # Read Data
    df = pd.read_excel(dev_data_path)

    all_dfs = []

    loops = df["corners"].count()

    for i in range(loops):

        temp_range = int(loops / 4)
        if i in range(0, temp_range):
            temp = 25
        elif i in range(temp_range, 2 * temp_range):
            temp = -40
        elif i in range(2 * temp_range, 3 * temp_range):
            temp = 125
        else:
            temp = 175

        tempr = []
        dev = []
        ic_meas = []
        ib_meas = []

        k = i
        if i >= len(devices):
            while k >= len(devices):
                k = k - len(devices)

        # Special case for 1st measured values

        if i == 0:

            idf_ic = df[["-vb ", "vc =-1", "vc =-2", "vc =-3"]].copy()
            idf_ic.rename(
                columns={
                    "-vb ": "measured_base_volt",
                    "vc =-1": "measured_ic_vcp_step1",
                    "vc =-2": "measured_ic_vcp_step2",
                    "vc =-3": "measured_ic_vcp_step3",
                },
                inplace=True,
            )

        else:

            idf_ic = df[
                ["-vb ", f"vc =-1.{2*i}", f"vc =-2.{2*i}", f"vc =-3.{2*i}"]
            ].copy()
            idf_ic.rename(
                columns={
                    "-vb ": "measured_base_volt",
                    f"vc =-1.{2*i}": "measured_ic_vcp_step1",
                    f"vc =-2.{2*i}": "measured_ic_vcp_step2",
                    f"vc =-3.{2*i}": "measured_ic_vcp_step3",
                },
                inplace=True,
            )

        os.makedirs(f"{dev_path}/ic_measured", exist_ok=True)
        idf_ic.to_csv(f"{dev_path}/ic_measured/measured_{devices[k]}_t{temp}.csv")

        idf_ib = df[
            ["-vb ", f"vc =-1.{2*i+1}", f"vc =-2.{2*i+1}", f"vc =-3.{2*i+1}"]
        ].copy()
        idf_ib.rename(
            columns={
                "-vb ": "measured_base_volt",
                f"vc =-1.{2*i+1}": "measured_ib_vcp_step1",
                f"vc =-2.{2*i+1}": "measured_ib_vcp_step2",
                f"vc =-3.{2*i+1}": "measured_ib_vcp_step3",
            },
            inplace=True,
        )

        os.makedirs(f"{dev_path}/ib_measured", exist_ok=True)
        idf_ib.to_csv(f"{dev_path}/ib_measured/measured_{devices[k]}_t{temp}.csv")

        dev.append(devices[k])
        tempr.append(temp)
        ic_meas.append(f"{dev_path}/ic_measured/measured_{devices[k]}_t{temp}.csv")
        ib_meas.append(f"{dev_path}/ib_measured/measured_{devices[k]}_t{temp}.csv")

        sdf = {
            "device": dev,
            "temp": tempr,
            "ic_measured": ic_meas,
            "ib_measured": ib_meas,
        }
        sdf = pd.DataFrame(sdf)
        all_dfs.append(sdf)

    df = pd.concat(all_dfs)
    df.dropna(axis=0, inplace=True)
    df["corner"] = "typical"
    df = df[["device", "temp", "corner", "ic_measured", "ib_measured"]]

    return df


def run_sim(char, dirpath, device, temp):
    """Run simulation at specific information and corner"""

    info = {}
    info["device"] = device
    info["temp"] = temp
    dev = device.split("_")[0]

    netlist_tmp = f"./device_netlists/{dev}.spice"

    temp_str = "{:.1f}".format(temp)

    netlist_path = f"{dirpath}/{dev}_netlists" + f"/netlist_{device}_t{temp_str}.spice"

    result_path_ib = f"{dirpath}/ib_simulated/" + f"simulated_{device}_t{temp_str}.csv"
    result_path_ic = f"{dirpath}/ic_simulated/" + f"simulated_{device}_t{temp_str}.csv"

    for c in char:
        os.makedirs(f"{dirpath}/{c}_simulated", exist_ok=True)

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
        if find_bjt(result_path_ib):
            bjt_simu_ib = result_path_ib
            bjt_simu_ic = result_path_ic
        else:
            bjt_simu_ib = "None"
            bjt_simu_ic = "None"
    except Exception:
        bjt_simu_ib = "None"
        bjt_simu_ic = "None"

    info["beta_sim_ib_unscaled"] = bjt_simu_ib
    info["beta_sim_ic_unscaled"] = bjt_simu_ic

    return info


def run_sims(char, df, dirpath, num_workers=mp.cpu_count()):

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures_list = []
        for j, row in df.iterrows():
            futures_list.append(
                executor.submit(run_sim, char, dirpath, row["device"], row["temp"])
            )

        for future in concurrent.futures.as_completed(futures_list):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logging.info(f"Test case generated an exception: {exc}")

    for c in char:
        sf = glob.glob(f"{dirpath}/{c}_simulated/*.csv")  # stored simulated data files

        for i in range(len(sf)):
            sdf = pd.read_csv(
                sf[i],
                header=None,
                delimiter=r"\s+",
            )

            sweep = len(pd.read_csv(glob.glob(f"{dirpath}/{c}_measured/*.csv")[1]))

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
                    0: "simulated_base_volt",
                    1: f"simulated_{c}_vcp_step1",
                    2: f"simulated_{c}_vcp_step2",
                    3: f"simulated_{c}_vcp_step3",
                },
                inplace=True,
            )

            sdf.to_csv(sf[i])

    df = pd.DataFrame(results)

    df = df[["device", "temp", "beta_sim_ib_unscaled", "beta_sim_ic_unscaled"]]
    df["beta_ib_sim"] = df["beta_sim_ib_unscaled"]
    df["beta_ic_sim"] = df["beta_sim_ic_unscaled"]

    return df


def main():
    """Main function applies all regression steps"""
    # ======= Checking ngspice  =======
    ngspice_v_ = os.popen("ngspice -v").read()
    if ngspice_v_ == "":
        logging.error("ngspice is not found. Please make sure ngspice is installed.")
        exit(1)
    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    main_regr_dir = "bjt_beta_regr"

    # bjt var.

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

    char = ["ib", "ic"]

    for i, dev in enumerate(devices):
        dev_path = f"{main_regr_dir}/{dev}"

        if os.path.exists(dev_path) and os.path.isdir(dev_path):
            shutil.rmtree(dev_path)

        os.makedirs(f"{dev_path}", exist_ok=False)

        logging.info("######" * 10)
        logging.info(f"# Checking Device {dev}")

        # for c in char :

        beta_data_files = glob.glob(
            f"../../180MCU_SPICE_DATA/BJT/bjt_{dev}_beta_f.nl_out.xlsx"
        )
        if len(beta_data_files) < 1:
            logging.info(f"# Can't find diode file for device: {dev}")
            beta_file = ""
        else:
            beta_file = os.path.abspath(beta_data_files[0])
        logging.info(f"# bjt_beta data points file : {beta_file}")

        if beta_file == "":
            logging.info(f"# No datapoints available for validation for device {dev}")
            continue

        if dev == "npn":
            f = ext_npn_measured
            list_dev = npn_devices
        elif dev == "pnp":
            f = ext_pnp_measured
            list_dev = pnp_devices

        if beta_file != "":
            meas_df = f(beta_file, dev, list_dev, dev_path)
        else:
            meas_df = []

        meas_len = len(pd.read_csv(glob.glob(f"{dev_path}/ic_measured/*.csv")[1]))

        logging.info(
            f"# Device {dev} number of measured_datapoints : {len(meas_df) * meas_len}"
        )

        sim_df = run_sims(char, meas_df, dev_path, 3)

        sim_len = len(
            pd.read_csv(glob.glob(f"{dev_path}/{char[1]}_simulated/*.csv")[1])
        )

        logging.info(
            f"# Device {dev} number of simulated datapoints : {len(sim_df) * sim_len}"
        )

        # compare section

        merged_df = meas_df.merge(sim_df, on=["device", "temp"], how="left")

        merged_all = []
        for c in char:

            merged_dfs = []

            for i in range(len(merged_df)):

                measured_data = pd.read_csv(merged_df[f"{c}_measured"][i])
                simulated_data = pd.read_csv(merged_df[f"beta_{c}_sim"][i])

                result_data = simulated_data.merge(measured_data, how="left")

                result_data["corner"] = "typical"
                result_data["device"] = (
                    merged_df[f"{c}_measured"][i]
                    .split("/")[-1]
                    .split("d_")[1]
                    .split("_t")[0]
                )
                result_data["temp"] = (
                    merged_df[f"{c}_measured"][i]
                    .split("/")[-1]
                    .split("_")[3]
                    .split("t")[1]
                    .split(".")[0]
                )

                result_data["step1_error"] = (
                    np.abs(
                        result_data[f"simulated_{c}_vcp_step1"]
                        - result_data[f"measured_{c}_vcp_step1"]
                    )
                    * 100.0
                    / result_data[f"measured_{c}_vcp_step1"]
                )

                result_data["step2_error"] = (
                    np.abs(
                        result_data[f"simulated_{c}_vcp_step2"]
                        - result_data[f"measured_{c}_vcp_step2"]
                    )
                    * 100.0
                    / result_data[f"measured_{c}_vcp_step2"]
                )

                result_data["step3_error"] = (
                    np.abs(
                        result_data[f"simulated_{c}_vcp_step3"]
                        - result_data[f"measured_{c}_vcp_step3"]
                    )
                    * 100.0
                    / result_data[f"measured_{c}_vcp_step3"]
                )

                result_data["error"] = (
                    np.abs(
                        result_data["step1_error"]
                        + result_data["step2_error"]
                        + result_data["step3_error"]
                    )
                    / 3
                )

                result_data = result_data[
                    [
                        "device",
                        "temp",
                        "corner",
                        "measured_base_volt",
                        f"measured_{c}_vcp_step1",
                        f"measured_{c}_vcp_step2",
                        f"measured_{c}_vcp_step3",
                        f"simulated_{c}_vcp_step1",
                        f"simulated_{c}_vcp_step2",
                        f"simulated_{c}_vcp_step3",
                        "step1_error",
                        "step2_error",
                        "step3_error",
                        "error",
                    ]
                ]

                merged_dfs.append(result_data)

            merged_out = pd.concat(merged_dfs)

            merged_out.to_csv(f"{dev_path}/error_analysis_{c}.csv", index=False)

            merged_all.append(merged_out)

        merged_all = pd.concat(merged_all)
        list_dev = npn_devices
        if dev == "pnp":
            list_dev = pnp_devices
        # calculating the error of each device and reporting it
        for dev in list_dev:
            min_error_total = float()
            max_error_total = float()
            error_total = float()
            number_of_existance = int()

            # number of rows in the final excel sheet
            num_rows = merged_all["device"].count()

            for n in range(num_rows):
                if dev == merged_all["device"].iloc[n]:
                    number_of_existance += 1
                    error_total += merged_all["error"].iloc[n]
                    if merged_all["error"].iloc[n] > max_error_total:
                        max_error_total = merged_all["error"].iloc[n]
                    elif merged_all["error"].iloc[n] < min_error_total:
                        min_error_total = merged_all["error"].iloc[n]

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
                logging.info(
                    f"# Device {dev} has failed regression. Needs more analysis."
                )


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
        format=f"%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Calling main function
    main()
