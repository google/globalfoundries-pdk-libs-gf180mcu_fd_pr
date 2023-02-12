"""
Globalfoundries 180u PCells Generator.

Usage:
    generate_pcell.py (--help| -h)
    generate_pcell.py (--device=<device_name>) [--thr=<thr>]

Options:
    --help -h                   Print this help message.
    --device=<device_name>      Select your device name. Allowed devices are (bjt , diode, MIM-A, MIM-B_gfB, MIM-B_gfC , fet, cap_mos, res)
    --thr=<thr>                 The number of threads used in run.
"""

from docopt import docopt
import os
import logging
import pandas as pd
import numpy as np


def draw_pcell(device_name):
    # draw pcells
    os.system(f"klayout -b -r draw_pcell.py -rd device_in={device_name}")


def main():

    # Device name used in gen.
    device_name = arguments["--device"]

    # Create output dir
    os.system("mkdir -p testcases")

    # Remove old output file
    file_path = f"testcases/{device_name}"
    if os.path.exists(file_path):
        os.system(f"rm -rf {file_path}")

    # gen csv patterns
    if device_name == "diode":
        diodes = [
            "diode_np",
            "diode_np_dn",
            "diode_pn",
            "diode_pn_dn",
            "diode_nw2ps",
            "diode_pw2dw",
            "diode_dw2ps",
            "diode_sc",
        ]
        for diode in diodes:
            draw_pcell(diode)

    elif device_name == "bjt":
        draw_pcell(device_name)

    elif device_name == "MIM-A":
        draw_pcell(device_name)

    elif "MIM-B" in device_name:
        draw_pcell(device_name)

    elif "fet" in device_name and "cap_" not in device_name:
        fet_devices = [
            "nfet_03v3",
            # "nfet_03v3_dn",
            # "nfet_05v0",
            # "nfet_05v0_dn",
            # "nfet_06v0",
            # "nfet_06v0_dn",
            "pfet_03v3",
            # "pfet_03v3_dn",
            # "pfet_05v0",
            # "pfet_05v0_dn",
            # "pfet_06v0",
            # "pfet_06v0_dn",
            # "nfet_06v0_nvt",
            # "nfet_10v0_asym",
            # "pfet_10v0_asym",
        ]
        for fet in fet_devices:
            draw_pcell(fet)

    elif device_name == "cap_mos":
        cap_mos_devices = [
            "cap_nmos",
            "cap_pmos",
            "cap_nmos_dn",
            "cap_pmos_dn",
            "cap_nmos_b",
            "cap_pmos_b",
        ]
        for cap_mos in cap_mos_devices:
            draw_pcell(cap_mos)

    elif device_name == "res":
        res_devices = [
            "nplus_u_resistor",
            "nplus_s_resistor",
            "pplus_u_resistor",
            "pplus_s_resistor",
            "nwell_resistor",
            "pwell_resistor",
            "npolyf_u_resistor",
            "npolyf_s_resistor",
            "ppolyf_u_resistor",
            "ppolyf_s_resistor",
            "ppolyf_u_high_Rs_resistor",
            "nplus_u_dw_resistor",
            "nplus_s_dw_resistor",
            "pplus_u_dw_resistor",
            "pplus_s_dw_resistor",
            "npolyf_u_dw_resistor",
            "npolyf_s_dw_resistor",
            "ppolyf_u_dw_resistor",
            "ppolyf_s_dw_resistor",
            "ppolyf_u_high_Rs_dw_resistor",
            "metal_resistor_rm1",
            "metal_resistor_rm2_3",
            "metal_resistor_tm9k",
            "metal_resistor_tm11k",
            "metal_resistor_tm30k",
        ]

        for res in res_devices:
            draw_pcell(res)
    else:
        pass


# ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================

if __name__ == "__main__":

    # logs format
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # arguments
    arguments = docopt(__doc__, version="PCELLS Gen.: 0.1")

    # No. of threads
    thrCount = (
        os.cpu_count() * 2 if arguments["--thr"] is None else int(arguments["--thr"])
    )

    # Calling main function
    main()
