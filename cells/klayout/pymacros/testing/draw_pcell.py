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

import os
import sys
import docopt

pcell_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, pcell_path)

import klayout.db as k
import pandas as pd
import math

from cells import gf180mcu

def draw_pcell(device_name, device_space):
    # dnwell layer
    # dnwell         = layout.layer(12 , 0 )

    # Read csv file for bjt patterns
    df = pd.read_csv(f"patterns/{device_name}_patterns.csv")

    # Count num. of patterns [instances]
    patterns_no = df.shape[0]
    pcell_row_no = int(math.sqrt(patterns_no))

    # inital value for instances location
    x_shift = 0
    y_shift = 0

    # Insert instance for each row
    for i, row in df.iterrows():

        # Get isntance location
        if (i % pcell_row_no) == 0:
            x_shift = 0 if i == 0 else x_shift + device_space * db_precession

        if (i % pcell_row_no) == 0:
            y_shift = 0
        else:
            y_shift = 0 if i == 0 else y_shift + device_space * db_precession
        
        param = row.to_dict()
        try:
            pcell_id = lib.layout().pcell_id(device_name)
            pc = layout.add_pcell_variant(lib, pcell_id, param)
            top.insert(k.CellInstArray(pc, k.Trans(x_shift, y_shift)))
        except Exception as e:
            print(f"Exception happened: {str(e)} for pattern {device_name} {param}")

    options = k.SaveLayoutOptions()
    options.write_context_info = False
    layout.write(f"testcases/{device_name}_pcells.gds", options)

def run_regression():
    # Set device name form env. variable
    device_pcell = "fet"  # noqa: F821

    # Instantiate and register the library
    gf180mcu()

    # Create new layout
    layout = k.Layout()

    # Used db unit in gds file
    db_precession = 1000

    # Create top cell
    top = layout.create_cell("TOP")

    # === Read gf180mcu pcells ===
    lib = k.Library.library_by_name("gf180mcu")

    # ======== BJT Gen. ========
    if device_pcell == "bjt":
        draw_pcell("bjt", 100)

    # ======== Diode Gen. ========
    if "diode" in device_pcell:
        if "pw2dw" in device_pcell or "dw2ps" in device_pcell:
            draw_pcell(device_pcell, 140)
        elif "_sc" in device_pcell:
            draw_pcell(device_pcell, 200)
        else:
            draw_pcell(device_pcell, 30)

    # ======== cap_mim Gen. ========
    if "MIM" in device_pcell:
        draw_pcell(device_pcell, 50)

    # ======== FET Gen. ========
    if "fet" in device_pcell and "cap_" not in device_pcell:
        if "10v0_asym" in device_pcell or "nvt" in device_pcell:
            draw_pcell(device_pcell, 450)
        else:
            draw_pcell(device_pcell, 250)

    # ======== cap_mos Gen. ========
    if "mos" in device_pcell and "cap_" in device_pcell:
        draw_pcell(device_pcell, 150)

    # ======== RES Gen. ========
    if "resistor" in device_pcell:
        draw_pcell(device_pcell, 50)


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

    