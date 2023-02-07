import os
import sys

device_name = "npn_00p54x02p00"

os.system(
    f"""
python3 run_lvs.py --design=../testcases/{device_name}_pcells.gds --net={device_name}_pcells.cdl --gf180mcu="A"
"""
)
