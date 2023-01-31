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
## Diode Pcells Generators for Klayout of GF180MCU
########################################################################################################################

import gdsfactory as gf
from .layers_def import *
from .via_generator import *


def draw_diode_nd2ps(
    layout,
    l: float = 0.1,
    w: float = 0.1,
    cw: float = 0.1,
    volt: str = "3.3V",
    deepnwell: bool = 0,
    pcmpgr: bool = 0,
) -> gf.Component:

    """
    Usage:-
     used to draw N+/LVPWELL diode (Outside DNWELL) by specifying parameters
    Arguments:-
     layout     : Object of layout
     l          : Float of diff length
     w          : Float of diff width
     cw         : Float of cathode width
     volt       : String of operating voltage of the diode [3.3V, 5V/6V]
     deepnwell  : Boolean of using Deep NWELL device
     pcmpgr     : Boolean of using P+ Guard Ring for Deep NWELL devices only
    """

    c = gf.Component("diode_nd2ps_dev")

    comp_spacing: float = 0.48
    np_enc_comp: float = 0.16
    pp_enc_comp: float = 0.16

    con_size = 0.22
    con_sp = 0.28
    con_comp_enc = 0.07

    dg_enc_cmp = 0.24
    dn_enc_lvpwell = 2.5
    lvpwell_enc_ncmp = 0.43
    lvpwell_enc_pcmp = 0.12

    # n generation
    ncmp = c.add_ref(gf.components.rectangle(size=(w, l), layer=comp_layer))
    nplus = c.add_ref(
        gf.components.rectangle(
            size=(
                ncmp.size[0] + (2 * np_enc_comp),
                ncmp.size[1] + (2 * np_enc_comp),
            ),
            layer=nplus_layer,
        )
    )
    nplus.xmin = ncmp.xmin - np_enc_comp
    nplus.ymin = ncmp.ymin - np_enc_comp
    diode_mk = c.add_ref(
        gf.components.rectangle(
            size=(ncmp.size[0], ncmp.size[1]), layer=diode_mk_layer
        )
    )
    diode_mk.xmin = ncmp.xmin
    diode_mk.ymin = ncmp.ymin

    ncmp_con = c.add_ref(
        via_stack(
            x_range=(ncmp.xmin, ncmp.xmax),
            y_range=(ncmp.ymin, ncmp.ymax),
            base_layer=comp_layer,
            metal_level=1,
        )
    )

    # p generation
    pcmp = c.add_ref(gf.components.rectangle(size=(cw, l), layer=comp_layer))
    pcmp.xmax = ncmp.xmin - comp_spacing
    pplus = c.add_ref(
        gf.components.rectangle(
            size=(
                pcmp.size[0] + (2 * pp_enc_comp),
                pcmp.size[1] + (2 * pp_enc_comp),
            ),
            layer=pplus_layer,
        )
    )
    pplus.xmin = pcmp.xmin - pp_enc_comp
    pplus.ymin = pcmp.ymin - pp_enc_comp

    pcmp_con = c.add_ref(
        via_stack(
            x_range=(pcmp.xmin, pcmp.xmax),
            y_range=(pcmp.ymin, pcmp.ymax),
            base_layer=comp_layer,
            metal_level=1,
        )
    )

    # creating layout and cell in klayout

    c.write_gds("diode_nd2ps_temp.gds")
    layout.read("diode_nd2ps_temp.gds")
    cell_name = "diode_nd2ps_dev"

    return layout.cell(cell_name)


# def draw_diode_pd2nw(layout, l, w, volt, deepnwell, pcmpgr):
#     """
#     Usage:-
#      used to draw 3.3V P+/Nwell diode (Outside DNWELL) by specifying parameters
#     Arguments:-
#      layout     : Object of layout
#      l          : Float of diffusion length
#      w          : Float of diffusion width
#      volt       : String of operating voltage of the diode [3.3V, 5V/6V]
#      deepnwell  : Boolean of using Deep NWELL device
#      pcmpgr     : Boolean of using P+ Guard Ring for Deep NWELL devices only
#     """


# def draw_diode_pw2dw(layout, l, w, volt):
#     """
#     Usage:-
#      used to draw LVPWELL/DNWELL diode by specifying parameters
#     Arguments:-
#      layout     : Object of layout
#      l          : Float of diff length
#      w          : Float of diff width
#      volt       : String of operating voltage of the diode [3.3V, 5V/6V]
#     """


# def draw_diode_dw2ps(layout, l, w, volt):
#     """
#     Usage:-
#      used to draw LVPWELL/DNWELL diode by specifying parameters
#     Arguments:-
#      layout     : Object of layout
#      l          : Float of diff length
#      w          : Float of diff width
#      volt       : String of operating voltage of the diode [3.3V, 5V/6V]
#     """
