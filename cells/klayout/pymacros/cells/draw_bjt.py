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
## BJT Pcells Generators for Klayout of GF180MCU
########################################################################################################################

import pya
import os

USER = os.environ['USER']
gds_path = f"/home/{USER}/.klayout/pymacros/cells/bjt"


def draw_npn(layout, device_name):

    if device_name == "npn_10p00x10p00":
        layout.read(f"{gds_path}/npn_10p00x10p00.gds")
        cell_name = "npn_10p00x10p00"
    elif device_name == "npn_05p00x05p00":
        layout.read(f"{gds_path}/npn_05p00x05p00.gds")
        cell_name = "npn_05p00x05p00"
    elif device_name == "npn_00p54x16p00":
        layout.read(f"{gds_path}/npn_00p54x16p00.gds")
        cell_name = "npn_00p54x16p00"
    elif device_name == "npn_00p54x08p00":
        layout.read(f"{gds_path}/npn_00p54x08p00.gds")
        cell_name = "npn_00p54x08p00"
    elif device_name == "npn_00p54x04p00":
        layout.read(f"{gds_path}/npn_00p54x04p00.gds")
        cell_name = "npn_00p54x04p00"
    elif device_name == "npn_00p54x02p00":
        layout.read(f"{gds_path}/npn_00p54x02p00.gds")
        cell_name = "npn_00p54x02p00"

    return layout.cell(cell_name)


def draw_pnp(layout, device_name):

    if device_name == "pnp_10p00x10p00":
        layout.read(f"{gds_path}/pnp_10p00x10p00.gds")
        cell_name = "pnp_10p00x10p00"
    elif device_name == "pnp_05p00x05p00":
        layout.read(f"{gds_path}/pnp_05p00x05p00.gds")
        cell_name = "pnp_05p00x05p00"
    elif device_name == "pnp_10p00x00p42":
        layout.read(f"{gds_path}/pnp_10p00x00p42.gds")
        cell_name = "pnp_10p00x00p42"
    elif device_name == "pnp_05p00x00p42":
        layout.read(f"{gds_path}/pnp_05p00x00p42.gds")
        cell_name = "pnp_05p00x00p42"

    return layout.cell(cell_name)

