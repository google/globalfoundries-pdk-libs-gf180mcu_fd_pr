"""
Globalfoundries 180u lvs test.

Usage:
    pcells_lvs_regression.py (--help| -h)
    pcells_lvs_regression.py (--device=<device_name>) [--thr=<thr>]

Options:
    --help -h                   Print this help message.
    --device=<device_name>      Select your device name.
    --thr=<thr>                 The number of threads used in run.
"""
from docopt import docopt
import os
import sys
from subprocess import check_call
import logging
import glob


def check_klayout_version():
    """
    check_klayout_version checks klayout version and makes sure it would work with the DRC.
    """
    # ======= Checking Klayout version =======
    klayout_v_ = os.popen("klayout -b -v").read()
    klayout_v_ = klayout_v_.split("\n")[0]
    klayout_v_list = []

    if klayout_v_ == "":
        logging.error("Klayout is not found. Please make sure klayout is installed.")
        exit(1)
    else:
        klayout_v_list = [int(v) for v in klayout_v_.split(" ")[-1].split(".")]

    logging.info(f"Your Klayout version is: {klayout_v_}")

    if len(klayout_v_list) < 1 or len(klayout_v_list) > 3:
        logging.error("Was not able to get klayout version properly.")
        exit(1)
    elif len(klayout_v_list) >= 2 or len(klayout_v_list) <= 3:
        if klayout_v_list[1] < 28:
            logging.error("Prerequisites at a minimum: KLayout 0.28.0")
            logging.error(
                "Using this klayout version has not been assesed in this development. Limits are unknown"
            )
            exit(1)

if __name__ == "__main__":

    ## Check Klayout version
    check_klayout_version()

    # arguments
    arguments = docopt(__doc__, version="PCELLS Gen.: 0.1")

    # No. of threads
    thrCount = os.cpu_count() * 2 if arguments["--thr"] is None else int(arguments["--thr"])

    device = arguments["--device"]
    run_lvs_full_path = "../../../../../rules/klayout/lvs"
    test_dir = f"{run_lvs_full_path}/testing/testcases"

    if "npn" in device:
        devices = ["npn_00p54x02p00"]
    else:
        devices = [device]

    res_data = []

    for device_name in devices:
        print(f"running lvs for {device_name}_pcells")

        call_str = f"""
        python3 {run_lvs_full_path}/run_lvs.py --design={test_dir}/{device_name}.gds --net={device_name}.cdl --gf180mcu="A" > {test_dir}/{device_name}.log
        """
        try:
            check_call(call_str, shell=True)
        except Exception as e:
            pattern_results = glob.glob(os.path.join(test_dir, f"{device_name}.lyrdb"))
            if len(pattern_results) < 1:
                logging.error("generated an exception")
                raise Exception("Failed LVS run.")
        
        print(f"reading {device_name} log")

        f = open(f"{run_lvs_full_path}/testing/testcases/{device_name}.log")
        log_data = f.readlines()
        f.close()
        print(log_data[-2])

        if "ERROR" in log_data[-2]:
            res_data.append((1, device_name))
        else:
            res_data.append((0, device_name))

    not_matched = []
    for dev_res in res_data:
        if dev_res[0] == 1:
            not_matched.append(f"{dev_res[1]}_pcells")

    if len(not_matched) > 0:
        print(f"not matched pcells : {not_matched}")
        exit(1)
