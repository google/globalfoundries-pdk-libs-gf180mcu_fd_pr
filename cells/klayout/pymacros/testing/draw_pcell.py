"""
Globalfoundries 180u PCells Generator.

Usage:
    draw_pcell.py (--help| -h)
    draw_pcell.py (--device=<device_name>)

Options:
    --help -h                   Print this help message.
    --device=<device_name>      Select your device name. Allowed devices are (bjt , diode, MIM-A, MIM-B_gfB, MIM-B_gfC , fet, cap_mos, res)
"""

import os
import sys
from docopt import docopt
import logging
pcell_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, pcell_path)

import klayout.db as k
import pandas as pd
import math
import glob

from cells import gf180mcu

DEV_SPACES = dict()
DEV_SPACES["fet"] = 450
DB_PERC = 1000

def draw_pcell(layout, top, lib, patt_file, device_name, device_space):
    # dnwell layer
    # dnwell         = layout.layer(12 , 0 )

    # Read csv file for bjt patterns
    df = pd.read_csv(patt_file)

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
            x_shift = 0 if i == 0 else x_shift + device_space * DB_PERC

        if (i % pcell_row_no) == 0:
            y_shift = 0
        else:
            y_shift = 0 if i == 0 else y_shift + device_space * DB_PERC
        
        param = row.to_dict()
        try:
            logging.info(f"Generating pcell for {device_name} with params : {param}")
            # pcell_id = lib.layout().pcell_id(device_name)
            pc = layout.add_pcell_variant(lib, device_name, param)
            top.insert(k.CellInstArray(pc, k.Trans(x_shift, y_shift)))
        except Exception as e:
            logging.error(f"Exception happened: {str(e)} for pattern {device_name} {param}")

def run_generation(target_device):

    file_path = os.path.dirname(os.path.abspath(__file__))
    list_patt_files = glob.glob(os.path.join(file_path, "patterns", target_device, "*.csv"))

    # Create new layout
    layout = k.Layout()

    # Create top cell
    top = layout.create_cell(f"{target_device}_pcells")

    # === Read gf180mcu pcells ===
    lib = k.Library.library_by_name("gf180mcu")

    
    for i,p in enumerate(list_patt_files):
        device = p.split("/")[-1].split("_patt")[0]
        device_type = device.split("_")[0]
        out_file = os.path.join(file_path, "testcases", f"{device}.gds")

        draw_pcell(layout, top, lib, p, device_type, DEV_SPACES[target_device])

        # Save the file
        options = k.SaveLayoutOptions()
        options.write_context_info = False
        layout.write(out_file, options)


if __name__ == "__main__":

    # logs format
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # arguments
    arguments = docopt(__doc__, version="PCELLS Gen.: 0.1")
    target_device = arguments["--device"]

    # Instantiate and register the library
    gf180mcu()

    # Calling main function
    run_generation(target_device)

    