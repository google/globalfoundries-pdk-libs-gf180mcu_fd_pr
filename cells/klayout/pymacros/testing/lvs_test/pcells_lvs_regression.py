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
