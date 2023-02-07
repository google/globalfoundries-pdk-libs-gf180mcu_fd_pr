import os
import sys

device_name = "npn_00p54x02p00"

os.system(
    f"""
klayout -b -r gf180mcu.lvs -rd input=../testcases/{device_name}_pcells.gds -rd report={device_name}_pcells.lyrdb -rd schematic={device_name}_pcells.cdl -rd target_netlist=extracted_netlist_{device_name}_pcells.cir
"""
)
