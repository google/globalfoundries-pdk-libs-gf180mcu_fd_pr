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

warnings.simplefilter(action="ignore", category=FutureWarning)


def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    os.system(f"Xyce -hspice-ext all {file_name} -l {file_name}.log")


def ext_measured(device, vn, d_in, cv_sim, corner, start, dirpath):

    # Get dimensions used for each device
    if "npn" in device:
        loops = 3
    else:
        loops = 2

    # Extracting measured values for each W & L
    for i in range(start, loops + start):

        # Special case for 1st measured values
        if i == 0:
            # measured Id
            col_list = [f"{vn}", f"{d_in}_{corner}"]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv", usecols=col_list)
            df_measured.columns = [f"{vn}", f"{d_in}_{corner}"]
            df_measured.to_csv(
                f"{dirpath}/measured_{cv_sim}/{i-start}_measured_{device}.csv",
                index=False,
            )
        else:
            # measured Id
            col_list = [f"{vn}", f"{d_in}_{corner}.{i}"]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv", usecols=col_list)
            df_measured.columns = [f"{vn}", f"{d_in}_{corner}"]
            df_measured.to_csv(
                f"{dirpath}/measured_{cv_sim}/{i-start}_measured_{device}.csv",
                index=False,
            )


def ext_simulated(device, vn, d_in, cv_sim, corner, temp, dirpath, cap):

    # Get dimensions used for each device
    netlist_tmp = f"./device_netlists/cv.spice"

    if "EBJ" in cap:
        i = 0
        if "npn" in device:
            connection = "0 out 0 0"
        else:
            connection = "0 0 out"
        Iopen = ""
    elif "CBJ" in cap:
        i = 1
        if "npn" in device:
            connection = "0 out open 0"
            Iopen = "Iopen open 0 0"
        else:
            connection = "0 0 out"
            Iopen = ""
    else:
        i = 2
        connection = "0 0 open out"
        Iopen = "Iopen open 0 0"

    with open(netlist_tmp) as f:
        tmpl = Template(f.read())
        os.makedirs(f"{dirpath}/{device}_netlists_{cv_sim}", exist_ok=True)
        with open(
            f"{dirpath}/{device}_netlists_{cv_sim}/{i}_{device}_netlist_{device}.spice",
            "w",
        ) as netlist:
            netlist.write(
                tmpl.render(
                    device=device,
                    i=i,
                    Iopen=Iopen,
                    connection=connection,
                    temp=temp,
                    cv_sim=cv_sim,
                    corner=corner,
                )
            )
        netlist_path = (
            f"{dirpath}/{device}_netlists_{cv_sim}/{i}_{device}_netlist_{device}.spice"
        )
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
                    if f"{i}_{device}_netlist_{device}.spice.ma" in x
                ]
            )
        ):
            with open(
                f"{dirpath}/{device}_netlists_{cv_sim}/{i}_{device}_netlist_{device}.spice.ma{j}"
            ) as f:
                freq = next(f).replace("FREQ = ", "")
                if "FAILED" in freq:
                    caps = 0
                else:
                    caps = 1000000 / (float(freq) * 2 * np.pi)
                df_simulated.append(caps)

        # zero array to append in it shaped (vn_sweeps, number of trials + 1)
        new_array = np.zeros((len(df_simulated), 2))
        new_array[: len(df_simulated), 0] = df_simulated
        new_array[: len(df_simulated), 1] = df_simulated

        # Writing final simulated data
        df_simulated = pd.DataFrame(new_array)
        if "npn_EBJ" in cap:
            df_cbj = pd.read_csv(
                f"{dirpath}/simulated_{cv_sim}/1_simulated_{device}.csv"
            )
            diff = df_simulated.iloc[:, 1] - df_cbj.iloc[:, 1]
            df_simulated = pd.DataFrame(
                data=[df_simulated.iloc[:, 0], diff]
            ).transpose()
            df_simulated.columns = [f"{vn}", f"{d_in}_{corner}"]
            df_simulated.to_csv(
                f"{dirpath}/simulated_{cv_sim}/{i}_simulated_{device}.csv", index=False
            )
        elif "pnp_CBJ" in cap:
            df_ebj = pd.read_csv(
                f"{dirpath}/simulated_{cv_sim}/0_simulated_{device}.csv"
            )
            diff = df_simulated.iloc[:, 1] - (2 * df_ebj.iloc[:, 1])
            df_simulated = pd.DataFrame(
                data=[df_simulated.iloc[:, 0], diff]
            ).transpose()
            df_simulated.columns = [f"{vn}", f"{d_in}_{corner}"]
            df_simulated.to_csv(
                f"{dirpath}/simulated_{cv_sim}/{i}_simulated_{device}.csv", index=False
            )
        else:
            df_simulated.columns = [f"{vn}", f"{d_in}_{corner}"]
            df_simulated.to_csv(
                f"{dirpath}/simulated_{cv_sim}/{i}_simulated_{device}.csv", index=False
            )


def error_cal(device, vn, d_in, cv_sim, corner, temp, dirpath):

    # Get dimensions used for each device
    if "npn" in device:
        loops = 3
    else:
        loops = 2
    df_final = pd.DataFrame()
    for i in range(0, loops):
        if i == 0:
            cap = "EBJ"
        elif i == 1:
            cap = "CBJ"
        else:
            cap = "CSJ"

        measured = pd.read_csv(f"{dirpath}/measured_{cv_sim}/{i}_measured_{device}.csv")
        simulated = pd.read_csv(
            f"{dirpath}/simulated_{cv_sim}/{i}_simulated_{device}.csv"
        )

        error_1 = round(
            100
            * abs(
                (abs(measured.iloc[:, 1]) - abs(simulated.iloc[:, 1]))
                / abs(measured.iloc[:, 1])
            ),
            6,
        )

        df_error = pd.DataFrame(data=[measured.iloc[:, 0], error_1]).transpose()
        df_error.to_csv(
            f"{dirpath}/error_{cv_sim}/{i}_{device}_error_{device}.csv", index=False
        )

        # Mean error
        mean_error = df_error[f"{d_in}_{corner}"].mean()
        # Max error
        max_error = df_error[f"{d_in}_{corner}"].max()
        # Max error location
        max_index = max((df_error == max_error).idxmax())
        max_location_vgs = (df_error == max_error).idxmax(axis=1)[max_index]
        max_location_vds = df_error[f"{vn}"][max_index]

        df_final_ = {
            "Run no.": f"{i}",
            "Temp": f"{temp}",
            "Device name": f"{device}",
            "corner": f"{corner}",
            "Junction": f"{cap}",
            "Simulated_Val": f"{cv_sim}",
            "Mean error%": f'{"{:.2f}".format(mean_error)}',
            "Max error%": f'{"{:.2f}".format(max_error)} @ {max_location_vgs} & vn (V) = {max_location_vds}',
        }
        df_final = df_final.append(df_final_, ignore_index=True)
    # Max mean error
    print(df_final)
    df_final.to_csv(f"{dirpath}/Final_report_{cv_sim}.csv", index=False)
    out_report = pd.read_csv(f"{dirpath}/Final_report_{cv_sim}.csv")
    print("\n", f"Max. mean error = {out_report['Mean error%'].max()}%")
    print(
        "====================================================================================================================================================="
    )


def main():

    # pandas setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    corners = ["typical", "ff", "ss"]
    temps = [25, -40, 100]
    measure = ["cv", "Vj", "bjt", 31]
    cv_sim, bjt_vn, bjt_in = measure[0], measure[1], measure[2]

    # npn
    npn_devices = [
        "npn_10p00x10p00",
        "npn_05p00x05p00",
        "npn_00p54x16p00",
        "npn_00p54x08p00",
        "npn_00p54x04p00",
        "npn_00p54x02p00",
    ]
    npn_start = 0

    for corner in corners:
        for temp in temps:
            for device in npn_devices:
                # Folder structure of measured values
                dirpath = f"{device}_{cv_sim}_{corner}_T{temp}"
                if os.path.exists(dirpath) and os.path.isdir(dirpath):
                    shutil.rmtree(dirpath)
                os.makedirs(f"{dirpath}/measured_{cv_sim}", exist_ok=False)

                # From xlsx to csv
                read_file = pd.read_excel(
                    f"../../180MCU_SPICE_DATA/BJT/{bjt_in}_{cv_sim}_npn.nl_out.xlsx"
                )
                read_file.to_csv(f"{dirpath}/{device}.csv", index=False, header=True)

                # Folder structure of simulated values
                os.makedirs(f"{dirpath}/simulated_{cv_sim}", exist_ok=False)
                os.makedirs(f"{dirpath}/error_{cv_sim}", exist_ok=False)
                ext_measured(device, bjt_vn, bjt_in, cv_sim, corner, npn_start, dirpath)
                ext_simulated(
                    device, bjt_vn, bjt_in, cv_sim, corner, temp, dirpath, "npn_CBJ"
                )
                ext_simulated(
                    device, bjt_vn, bjt_in, cv_sim, corner, temp, dirpath, "npn_EBJ"
                )
                ext_simulated(
                    device, bjt_vn, bjt_in, cv_sim, corner, temp, dirpath, "npn_CSJ"
                )
                error_cal(device, bjt_vn, bjt_in, cv_sim, corner, temp, dirpath)

                npn_start = npn_start + 3
        npn_start = 0

    # pnp
    pnp_devices = [
        "pnp_10p00x00p42",
        "pnp_05p00x00p42",
        "pnp_10p00x10p00",
        "pnp_05p00x05p00",
    ]
    pnp_start = 0

    for corner in corners:
        for temp in temps:
            for device in pnp_devices:
                # Folder structure of measured values
                dirpath = f"{device}_{cv_sim}_{corner}_T{temp}"
                if os.path.exists(dirpath) and os.path.isdir(dirpath):
                    shutil.rmtree(dirpath)
                os.makedirs(f"{dirpath}/measured_{cv_sim}", exist_ok=False)

                # From xlsx to csv
                read_file = pd.read_excel(
                    f"../../180MCU_SPICE_DATA/BJT/{bjt_in}_{cv_sim}_pnp.nl_out.xlsx"
                )
                read_file.to_csv(f"{dirpath}/{device}.csv", index=False, header=True)

                # Folder structure of simulated values
                os.makedirs(f"{dirpath}/simulated_{cv_sim}", exist_ok=False)
                os.makedirs(f"{dirpath}/error_{cv_sim}", exist_ok=False)
                ext_measured(device, bjt_vn, bjt_in, cv_sim, corner, pnp_start, dirpath)
                ext_simulated(
                    device, bjt_vn, bjt_in, cv_sim, corner, temp, dirpath, "pnp_EBJ"
                )
                ext_simulated(
                    device, bjt_vn, bjt_in, cv_sim, corner, temp, dirpath, "pnp_CBJ"
                )
                error_cal(device, bjt_vn, bjt_in, cv_sim, corner, temp, dirpath)

                pnp_start = pnp_start + 2
        pnp_start = 0


# # ================================================================
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
