"""
Globalfoundries 180u lvs test.

Usage:
    lvs_test.py (--help| -h)
    lvs_test.py (--device=<device_name>) [--thr=<thr>]

Options:
    --help -h                   Print this help message.
    --device=<device_name>      Select your device name.
    --thr=<thr>                 The number of threads used in run.
"""
from docopt import docopt
import os
import sys

# arguments
arguments = docopt(__doc__, version="PCELLS Gen.: 0.1")

# No. of threads
thrCount = os.cpu_count() * 2 if arguments["--thr"] is None else int(arguments["--thr"])

device = arguments["--device"]
test_dir = "../testcases"

if "npn" in device:
    devices = ["npn_00p54x02p00", "rm1"]
else:
    devices = [device]

res_data = []

for device_name in devices:
    print(f"running lvs for {device_name}_pcells")
    os.system(
        f"""
    klayout -b -r gf180mcu.lvs -rd input={test_dir}/{device_name}_pcells.gds -rd report={device_name}_pcells.lyrdb -rd schematic={device_name}_pcells.cdl -rd target_netlist=extracted_netlist_{device_name}_pcells.cir > {test_dir}/{device_name}_pcells.log
    """
    )
    print(f"reading {device_name}_pcells log")

    f = open(f"{test_dir}/{device_name}_pcells.log")
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
