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
thrCount = (
    os.cpu_count() * 2 if arguments["--thr"] is None else int(arguments["--thr"])
)

device_name = arguments["--device"]

os.system(
    f"""
klayout -b -r gf180mcu.lvs -rd input=../testcases/{device_name}_pcells.gds -rd report={device_name}_pcells.lyrdb -rd schematic={device_name}_pcells.cdl -rd target_netlist=extracted_netlist_{device_name}_pcells.cir
"""
)
