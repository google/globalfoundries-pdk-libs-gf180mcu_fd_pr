# Copyright 2022 GlobalFoundries PDK Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

########################################################################################################################
## Pcells test Generators for Klayout of GF180MCU
########################################################################################################################

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
import klayout.db as k
import pandas as pd
import math
import glob
import json

pcell_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, pcell_path)

from cells import gf180mcu  # noqa E402

# DEV_SPACES = dict()
# DEV_SPACES["fet"] = 450
DB_PERC = 1000


def draw_pcell(layout, top, lib, patt_file, device_name, device_space):
    """
    draws pcell using klayout pymacros

    Args :
        layout : layout object
        top : layout top cell
        lib : pcells library
        patt_file : patterns csv file path
        device_name : name of the device under test
        device_space : device instances spacing
    """

    # Read csv file of patterns
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

        pcell_name = row["pcell_name"]

        if "fet" in device_name:
            param = row.drop(
                labels=[
                    "pcell_name",
                    "netlist_name",
                    "netlist_nets",
                    "netlists_param",
                    "dev_name",
                ]
            ).to_dict()

            param["g_lbl"] = param["g_lbl"].split("_")
            param["sd_lbl"] = param["sd_lbl"].split("_")

        else:

            param = row.drop(labels=["pcell_name"]).to_dict()

        try:
            logging.info(f"Generating pcell for {device_name} with params : {param}")
            pcell_id = lib.layout().pcell_id(pcell_name)
            pc = layout.add_pcell_variant(lib, pcell_id, param)
            top.insert(k.CellInstArray(pc, k.Trans(x_shift, y_shift)))
        except Exception as e:
            logging.error(
                f"Exception happened: {str(e)} for pattern {device_name} {param}"
            )


def run_generation(target_device):
    """
    Runs generation of the device under test

    Args :
        target_device : category of device under test
    """

    file_path = os.path.dirname(os.path.abspath(__file__))
    list_patt_files = glob.glob(
        os.path.join(file_path, "patterns", target_device, "*.csv")
    )

    # === Read gf180mcu pcells ===
    lib = k.Library.library_by_name("gf180mcu")

    for p in list_patt_files:

        # Get device_name
        device = p.split("/")[-1].split("_patt")[0]

        # Create output file
        os.makedirs(f"{file_path}/testcases", exist_ok=True)
        out_file = os.path.join(file_path, "testcases", f"{device}_pcells.gds")

        # Read device setting
        dev_setting = json.load(open(f"{file_path}/patterns/{target_device}.json"))

        # Create new layout
        layout = k.Layout()

        # Create top cell
        top = layout.create_cell(f"{device}_pcells")

        # Call draww_pcell
        draw_pcell(layout, top, lib, p, device, dev_setting["spacing"])

        # Flatten cell
        top.flatten(1)

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
