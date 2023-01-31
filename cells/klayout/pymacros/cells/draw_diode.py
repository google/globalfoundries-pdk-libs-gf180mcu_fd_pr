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
    lvpwell_enc_ncmp = 0.6
    lvpwell_enc_pcmp = 0.16
    pcmpgr_enc_dn = 2.5

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

    if volt == "5/6V":
        dg = c.add_ref(
            gf.components.rectangle(
                size=(
                    ncmp.xmax - pcmp.xmin + (2 * dg_enc_cmp),
                    ncmp.size[1] + (2 * dg_enc_cmp),
                ),
                layer=dualgate_layer,
            )
        )
        dg.xmin = pcmp.xmin - dg_enc_cmp
        dg.ymin = pcmp.ymin - dg_enc_cmp

    if deepnwell == 1:
        lvpwell = c.add_ref(
            gf.components.rectangle(
                size=(
                    ncmp.xmax
                    - pcmp.xmin
                    + (lvpwell_enc_ncmp + lvpwell_enc_pcmp),
                    ncmp.size[1] + (2 * lvpwell_enc_ncmp),
                ),
                layer=lvpwell_layer,
            )
        )

        lvpwell.xmin = pcmp.xmin - lvpwell_enc_pcmp
        lvpwell.ymin = ncmp.ymin - lvpwell_enc_ncmp

        dn_rect = c.add_ref(
            gf.components.rectangle(
                size=(
                    lvpwell.size[0] + (2 * dn_enc_lvpwell),
                    lvpwell.size[1] + (2 * dn_enc_lvpwell),
                ),
                layer=dnwell_layer,
            )
        )

        dn_rect.xmin = lvpwell.xmin - dn_enc_lvpwell
        dn_rect.ymin = lvpwell.ymin - dn_enc_lvpwell

        if pcmpgr == 1:

            c_temp_gr = gf.Component("temp_store guard ring")
            rect_pcmpgr_in = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (dn_rect.xmax - dn_rect.xmin) + 2 * pcmpgr_enc_dn,
                        (dn_rect.ymax - dn_rect.ymin) + 2 * pcmpgr_enc_dn,
                    ),
                    layer=comp_layer,
                )
            )
            rect_pcmpgr_in.move(
                (dn_rect.xmin - pcmpgr_enc_dn, dn_rect.ymin - pcmpgr_enc_dn)
            )
            rect_pcmpgr_out = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * cw,
                        (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * cw,
                    ),
                    layer=comp_layer,
                )
            )
            rect_pcmpgr_out.move(
                (rect_pcmpgr_in.xmin - cw, rect_pcmpgr_in.ymin - cw)
            )
            B = c.add_ref(
                gf.geometry.boolean(
                    A=rect_pcmpgr_out,
                    B=rect_pcmpgr_in,
                    operation="A-B",
                    layer=comp_layer,
                )
            )

            psdm_in = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin)
                        - 2 * pp_enc_comp,
                        (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin)
                        - 2 * pp_enc_comp,
                    ),
                    layer=pplus_layer,
                )
            )
            psdm_in.move(
                (
                    rect_pcmpgr_in.xmin + pp_enc_comp,
                    rect_pcmpgr_in.ymin + pp_enc_comp,
                )
            )
            psdm_out = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (rect_pcmpgr_out.xmax - rect_pcmpgr_out.xmin)
                        + 2 * pp_enc_comp,
                        (rect_pcmpgr_out.ymax - rect_pcmpgr_out.ymin)
                        + 2 * pp_enc_comp,
                    ),
                    layer=pplus_layer,
                )
            )
            psdm_out.move(
                (
                    rect_pcmpgr_out.xmin - pp_enc_comp,
                    rect_pcmpgr_out.ymin - pp_enc_comp,
                )
            )
            psdm = c.add_ref(
                gf.geometry.boolean(
                    A=psdm_out, B=psdm_in, operation="A-B", layer=pplus_layer
                )
            )

            # generating contacts

            ring_con_bot = c.add_ref(
                via_generator(
                    x_range=(
                        rect_pcmpgr_in.xmin + con_size,
                        rect_pcmpgr_in.xmax - con_size,
                    ),
                    y_range=(rect_pcmpgr_out.ymin, rect_pcmpgr_in.ymin),
                    via_enclosure=(con_comp_enc, con_comp_enc),
                    via_layer=contact_layer,
                    via_size=(con_size, con_size),
                    via_spacing=(con_sp, con_sp),
                )
            )

            ring_con_up = c.add_ref(
                via_generator(
                    x_range=(
                        rect_pcmpgr_in.xmin + con_size,
                        rect_pcmpgr_in.xmax - con_size,
                    ),
                    y_range=(rect_pcmpgr_in.ymax, rect_pcmpgr_out.ymax),
                    via_enclosure=(con_comp_enc, con_comp_enc),
                    via_layer=contact_layer,
                    via_size=(con_size, con_size),
                    via_spacing=(con_sp, con_sp),
                )
            )

            ring_con_r = c.add_ref(
                via_generator(
                    x_range=(rect_pcmpgr_out.xmin, rect_pcmpgr_in.xmin),
                    y_range=(
                        rect_pcmpgr_in.ymin + con_size,
                        rect_pcmpgr_in.ymax - con_size,
                    ),
                    via_enclosure=(con_comp_enc, con_comp_enc),
                    via_layer=contact_layer,
                    via_size=(con_size, con_size),
                    via_spacing=(con_sp, con_sp),
                )
            )

            ring_con_l = c.add_ref(
                via_generator(
                    x_range=(rect_pcmpgr_in.xmax, rect_pcmpgr_out.xmax),
                    y_range=(
                        rect_pcmpgr_in.ymin + con_size,
                        rect_pcmpgr_in.ymax - con_size,
                    ),
                    via_enclosure=(con_comp_enc, con_comp_enc),
                    via_layer=contact_layer,
                    via_size=(con_size, con_size),
                    via_spacing=(con_sp, con_sp),
                )
            )

            comp_m1_in = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(rect_pcmpgr_in.size[0], rect_pcmpgr_in.size[1]),
                    layer=m1_layer,
                )
            )

            comp_m1_out = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * cw,
                        (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * cw,
                    ),
                    layer=m1_layer,
                )
            )
            comp_m1_out.move(
                (rect_pcmpgr_in.xmin - cw, rect_pcmpgr_in.ymin - cw)
            )
            m1 = c.add_ref(
                gf.geometry.boolean(
                    A=rect_pcmpgr_out,
                    B=rect_pcmpgr_in,
                    operation="A-B",
                    layer=m1_layer,
                )
            )

    # creating layout and cell in klayout

    c.write_gds("diode_nd2ps_temp.gds")
    layout.read("diode_nd2ps_temp.gds")
    cell_name = "diode_nd2ps_dev"

    return layout.cell(cell_name)
