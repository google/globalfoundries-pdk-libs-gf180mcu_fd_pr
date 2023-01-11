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

warnings.simplefilter(action="ignore", category=FutureWarning)
PASS_THRESH = 2.0


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    os.system(f"Xyce -hspice-ext all {file_name} -l {file_name}.log 2> /dev/null")


def ext_measured(device: str, cv_sim: str, corner: str, start: int) -> None:
    """ext_measured function calculates get measured data

    Args:
        device (str): device name
        cv_sim (str): cv simulation
        corner (str): corner name
        start (int): start point
    """

    # Get dimensions used for each device
    dirpath = f"mimcap_c/{device}_{cv_sim}_{corner}"

    # Extracting measured values for each W & L
    for i in range(start, 4 + start):
        if i == 0 + start:
            width = 100
            length = 100
        if i == 1 + start:
            width = 5
            length = 5
        if i == 2 + start:
            width = 100
            length = 5
        if i == 3 + start:
            width = 5
            length = 100

        if i == 0:
            # measured cv
            col_list = ["Vj", f"mimcap_{corner}"]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv", usecols=col_list)
            df_measured.to_csv(
                f"{dirpath}/measured_{cv_sim}/{i-start}_measured_w{width}_l{length}.csv",
                index=False,
            )
        else:
            # measured cv
            col_list = ["Vj", f"mimcap_{corner}.{i}"]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv", usecols=col_list)
            df_measured.columns = ["Vj", f"mimcap_{corner}"]
            df_measured.to_csv(
                f"{dirpath}/measured_{cv_sim}/{i-start}_measured_w{width}_l{length}.csv",
                index=False,
            )


def ext_simulated(
    device: str, cv_sim: str, corner: str, start: int, voltage: str
) -> None:
    """ext_simulated function calculates get simulated data
    Args:
        device (str): device name
        cv_sim (str): cv simulation
        corner (str): corner name
        start (int): start point
        voltage (str): voltage sweep
    """
    # Get dimensions used for each device
    dirpath = f"mimcap_c/{device}_{cv_sim}_{corner}"
    netlist_tmp = "./device_netlists/mimcap.spice"

    # Extracting measured values for each W & L
    for i in range(start, 4 + start):
        if i == 0 + start:
            width = 100
            length = 100
        if i == 1 + start:
            width = 5
            length = 5
        if i == 2 + start:
            width = 100
            length = 5
        if i == 3 + start:
            width = 5
            length = 100

        with open(netlist_tmp) as f:
            tmpl = Template(f.read())
            os.makedirs(f"{dirpath}/{device}_netlists_{cv_sim}", exist_ok=True)
            with open(
                f"{dirpath}/{device}_netlists_{cv_sim}/{i-start}_{device}_netlist_w{width}_l{length}.spice",
                "w",
            ) as netlist:
                netlist.write(
                    tmpl.render(
                        device=device,
                        width=width,
                        length=length,
                        corner=corner,
                        voltage=voltage,
                    )
                )
            netlist_path = f"{dirpath}/{device}_netlists_{cv_sim}/{i-start}_{device}_netlist_w{width}_l{length}.spice"
            # Running ngspice for each netlist
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=workers_count
            ) as executor:
                executor.submit(call_simulator, netlist_path)

        # Writing simulated data
        df_simulated = []
        # Writing simulated data
        for j in range(
            len(
                [
                    x
                    for x in os.listdir(f"{dirpath}/{device}_netlists_{cv_sim}")
                    if f"{i-start}_{device}_netlist_w{width}_l{length}.spice.ma" in x
                ]
            )
        ):
            with open(
                f"{dirpath}/{device}_netlists_{cv_sim}/{i-start}_{device}_netlist_w{width}_l{length}.spice.ma{j}"
            ) as f:
                cap = 1000000 / (float(next(f).replace("FREQ = ", "")) * 2 * np.pi)
                df_simulated.append(cap)

        # zero array to append in it shaped (vn_sweeps, number of trials + 1)
        new_array = np.zeros((len(df_simulated), 2))
        new_array[: len(df_simulated), 0] = df_simulated
        new_array[: len(df_simulated), 1] = df_simulated

        # Writing final simulated data
        df_simulated = pd.DataFrame(new_array)
        df_simulated.columns = ["Vj", f"mimcap_{corner}"]
        df_simulated.to_csv(
            f"{dirpath}/simulated_{cv_sim}/{i-start}_simulated_w{width}_l{length}.csv",
            index=False,
        )


def error_cal(device: str, Id_sim: str, corner: str, start: int) -> None:
    """error function calculates the error between measured, simulated data
    Args:
        device (str): device name
        Id_sim (str): cv simulation
        corner (str): corner name
        start (int): start point
    """
    # Get dimensions used for each device
    dirpath = f"mimcap_c/{device}_{Id_sim}_{corner}"
    df_final = pd.DataFrame()
    for i in range(start, 4 + start):
        if i == 0 + start:
            width = 100
            length = 100
        if i == 1 + start:
            width = 5
            length = 5
        if i == 2 + start:
            width = 100
            length = 5
        if i == 3 + start:
            width = 5
            length = 100

        measured = pd.read_csv(
            f"{dirpath}/measured_{Id_sim}/{i-start}_measured_w{width}_l{length}.csv"
        )
        simulated = pd.read_csv(
            f"{dirpath}/simulated_{Id_sim}/{i-start}_simulated_w{width}_l{length}.csv"
        )

        error_1 = round(
            100
            * abs(
                (abs(measured.iloc[:, 1]) - abs(simulated.iloc[:, 1]))
                / abs(measured.iloc[:, 1])
            ),
            8,
        )

        df_error = pd.DataFrame(data=[measured.iloc[:, 0], error_1]).transpose()
        df_error.to_csv(
            f"{dirpath}/error_{Id_sim}/{i-start}_{device}_error_w{width}_l{length}.csv",
            index=False,
        )

        # Mean error
        mean_error = df_error[f"mimcap_{corner}"].mean()
        # Max error
        max_error = df_error[f"mimcap_{corner}"].max()

        df_final_ = {
            "Run no.": f"{i-start}",
            "Device name": f"{dirpath}",
            "Width": f"{width}",
            "Length": f"{length}",
            "Simulated_Val": f"{Id_sim}",
            "Mean error%": f'{"{:.2f}".format(mean_error)}',
            "Max error%": f'{"{:.2f}".format(max_error)} ',
        }
        df_final = df_final.append(df_final_, ignore_index=True)

    # Max mean error
    df_final.to_csv(f"{dirpath}/Final_report_{Id_sim}.csv", index=False)
    # logging.infoing min, max, mean errors to the consol

    out_report = pd.read_csv(f"{dirpath}/Final_report_{Id_sim}.csv")

    # Making sure that min, max, mean errors are not > 100%
    mean_error_total = out_report["Mean error%"].mean()
    max_error_total = out_report["Max error%"].max()
    if max_error_total > 100:
        max_error_total = 100

    if mean_error_total > 100:
        mean_error_total = 100

    logging.info(
        f"# Device {device}_{corner} mean error: {mean_error_total:.2f}, max error {max_error_total:.2f}"
    )

    if max_error_total < PASS_THRESH:
        logging.info(f"# Device {device} {corner} has passed regression.")
    else:
        logging.error(f"# Device {device} {corner} has failed regression.")


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

    corners = ["ss", "typical", "ff"]
    devices = [
        "cap_mim_1f5_m2m3_noshield",
        "cap_mim_1f0_m3m4_noshield",
        "cap_mim_2f0_m4m5_noshield",
    ]
    measure = ["cv", "corners", "CV (fF)"]
    voltage = ["-3.0 3.0 0.1"]
    start = 0
    for corner in corners:
        for device in devices:
            # Folder structure of measured values
            cv_sim = measure[0]
            dirpath = f"mimcap_c/{device}_{cv_sim}_{corner}"
            if os.path.exists(dirpath) and os.path.isdir(dirpath):
                shutil.rmtree(dirpath)
            os.makedirs(f"{dirpath}/measured_{cv_sim}", exist_ok=False)

            logging.info("######" * 10)
            logging.info(f"# Checking Device {device}_{corner}")

            # From xlsx to csv
            read_file = pd.read_excel(
                "../../180MCU_SPICE_DATA/Cap/mimcap_fc.nl_out.xlsx"
            )
            read_file.to_csv(f"{dirpath}/{device}.csv", index=False, header=True)

            # Folder structure of simulated values
            os.makedirs(f"{dirpath}/simulated_{cv_sim}", exist_ok=False)
            os.makedirs(f"{dirpath}/error_{cv_sim}", exist_ok=False)

            ext_measured(device, cv_sim, corner, start)
            ext_simulated(device, cv_sim, corner, start, voltage[0])
            error_cal(device, cv_sim, corner, start)
            start = start + 4
        start = 0


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
