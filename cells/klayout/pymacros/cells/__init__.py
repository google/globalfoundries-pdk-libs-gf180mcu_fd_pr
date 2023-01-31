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

# ============================================================================
# ---------------- Pcells Generators for Klayout of GF180MCU ----------------
# ============================================================================

import pya

from .fet import *
from .diode import *
from .bjt import *
from .cap_mos import *
from .cap_mim import *
from .res import *
from .efuse import *


# It's a Python class that inherits from the pya.Library class
class gf180mcu(pya.Library):
    """
    The library where we will put the PCell into
    """

    def __init__(self):
        # Set the description
        self.description = "GF180MCU Pcells"

        # Create the PCell declarations
        # MOS DEVICES
        self.layout().register_pcell(
            "nfet", nfet()
        )  # nfet_03v3 , nfet_05v0 , nfet_06v0
        self.layout().register_pcell(
            "pfet", pfet()
        )  # pfet_03v3 , pfet_05v0 , pfet_06v0
        self.layout().register_pcell("nfet_06v0_nvt", nfet_06v0_nvt())
        # self.layout().register_pcell("nfet_10v0_asym", nfet_10v0_asym())
        # self.layout().register_pcell("pfet_10v0_asym", pfet_10v0_asym())

        # BJT
        self.layout().register_pcell(
            "npn_bjt", npn_bjt()
        )  # npn_10p00x10p00 , npn_05p00x05p00 , npn_00p54x16p00 ,
           # npn_00p54x08p00 , npn_00p54x04p00 , npn_00p54x02p00
        self.layout().register_pcell(
            "pnp_bjt", pnp_bjt()
        )  # pnp_10p00x10p00 , pnp_05p00x05p00 , pnp_10p00x00p42 , pnp_05p00x00p42

        # DIODE DEVICES
        self.layout().register_pcell(
            "diode_nd2ps", diode_nd2ps()
        )  # diode_nd2ps_03v3    , diode_nd2ps_06v0
        self.layout().register_pcell(
            "diode_pd2nw", diode_pd2nw()
        )  # diode_pd2nw_03v3    , diode_pd2nw_06v0
        self.layout().register_pcell(
            "diode_nw2ps", diode_nw2ps()
        )  # diode_nw2ps_03v3   , diode_nw2ps_06v0
        self.layout().register_pcell(
            "diode_pw2dw", diode_pw2dw()
        )  # diode_pw2dw_03v3 , diode_pw2dw_06v0
        self.layout().register_pcell(
            "diode_dw2ps", diode_dw2ps()
        )  # diode_dw2ps_03v3 , diode_dw2ps_06v0

        # Register us with the name "gf180mcu".
        self.register("gf180mcu")
