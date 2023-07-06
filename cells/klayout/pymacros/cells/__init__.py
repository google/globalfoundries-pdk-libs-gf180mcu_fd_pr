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

from .fet import nfet, pfet, nfet_06v0_nvt
from .diode import (
    diode_dw2ps,
    diode_nd2ps,
    diode_nw2ps,
    diode_pd2nw,
    diode_pw2dw,
    sc_diode,
)
from .bjt import npn_bjt, pnp_bjt
from .cap_mos import cap_nmos, cap_nmos_b, cap_pmos, cap_pmos_b
from .cap_mim import cap_mim
from .res import (
    metal_resistor,
    nplus_s_resistor,
    nplus_u_resistor,
    pplus_s_resistor,
    pplus_u_resistor,
    npolyf_s_resistor,
    npolyf_u_resistor,
    ppolyf_s_resistor,
    ppolyf_u_resistor,
    ppolyf_u_high_Rs_resistor,
    nwell_resistor,
    pwell_resistor,
)
from .efuse import efuse
from .vias_gen import via_dev


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
        self.layout().register_pcell("sc_diode", sc_diode())

        # MIM_CAP DEVICES
        self.layout().register_pcell("cap_mim", cap_mim())

        # cap_mos
        self.layout().register_pcell(
            "cap_nmos", cap_nmos()
        )  # cap_nmos_03v3   , cap_nmos_06v0
        self.layout().register_pcell(
            "cap_pmos", cap_pmos()
        )  # cap_pmos_03v3   , cap_pmos_06v0
        self.layout().register_pcell(
            "cap_nmos_b", cap_nmos_b()
        )  # cap_nmos_03v3_b , cap_nmos_06v0_b
        self.layout().register_pcell(
            "cap_pmos_b", cap_pmos_b()
        )  # cap_pmos_03v3_b , cap_pmos_06v0_b

        # RES
        self.layout().register_pcell("metal_resistor", metal_resistor())
        self.layout().register_pcell("nplus_s_resistor", nplus_s_resistor())
        self.layout().register_pcell("pplus_s_resistor", pplus_s_resistor())
        self.layout().register_pcell("nplus_u_resistor", nplus_u_resistor())
        self.layout().register_pcell("pplus_u_resistor", pplus_u_resistor())
        self.layout().register_pcell("nwell_resistor", nwell_resistor())
        self.layout().register_pcell("pwell_resistor", pwell_resistor())
        self.layout().register_pcell("npolyf_s_resistor", npolyf_s_resistor())
        self.layout().register_pcell("ppolyf_s_resistor", ppolyf_s_resistor())
        self.layout().register_pcell("npolyf_u_resistor", npolyf_u_resistor())
        self.layout().register_pcell("ppolyf_u_resistor", ppolyf_u_resistor())
        self.layout().register_pcell(
            "ppolyf_u_high_Rs_resistor", ppolyf_u_high_Rs_resistor()
        )

        # VIAS
        self.layout().register_pcell("via_dev", via_dev())

        # Register us with the name "gf180mcu".
        self.register("gf180mcu")
