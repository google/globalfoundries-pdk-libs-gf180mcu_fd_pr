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
from .layers_def import layer
from .via_generator import via_generator, via_stack

import numpy as np


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
    ncmp = c.add_ref(gf.components.rectangle(size=(w, l), layer=layer["comp"]))
    nplus = c.add_ref(
        gf.components.rectangle(
            size=(ncmp.size[0] + (2 * np_enc_comp), ncmp.size[1] + (2 * np_enc_comp),),
            layer=layer["nplus"],
        )
    )
    nplus.xmin = ncmp.xmin - np_enc_comp
    nplus.ymin = ncmp.ymin - np_enc_comp
    diode_mk = c.add_ref(
        gf.components.rectangle(
            size=(ncmp.size[0], ncmp.size[1]), layer=layer["diode_mk"]
        )
    )
    diode_mk.xmin = ncmp.xmin
    diode_mk.ymin = ncmp.ymin

    ncmp_con = c.add_ref(
        via_stack(
            x_range=(ncmp.xmin, ncmp.xmax),
            y_range=(ncmp.ymin, ncmp.ymax),
            base_layer=layer["comp"],
            metal_level=1,
        )
    )

    # p generation
    pcmp = c.add_ref(gf.components.rectangle(size=(cw, l), layer=layer["comp"]))
    pcmp.xmax = ncmp.xmin - comp_spacing
    pplus = c.add_ref(
        gf.components.rectangle(
            size=(pcmp.size[0] + (2 * pp_enc_comp), pcmp.size[1] + (2 * pp_enc_comp),),
            layer=layer["pplus"],
        )
    )
    pplus.xmin = pcmp.xmin - pp_enc_comp
    pplus.ymin = pcmp.ymin - pp_enc_comp

    pcmp_con = c.add_ref(
        via_stack(
            x_range=(pcmp.xmin, pcmp.xmax),
            y_range=(pcmp.ymin, pcmp.ymax),
            base_layer=layer["comp"],
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
                layer=layer["dualgate"],
            )
        )
        dg.xmin = pcmp.xmin - dg_enc_cmp
        dg.ymin = pcmp.ymin - dg_enc_cmp

    if deepnwell == 1:
        lvpwell = c.add_ref(
            gf.components.rectangle(
                size=(
                    ncmp.xmax - pcmp.xmin + (lvpwell_enc_ncmp + lvpwell_enc_pcmp),
                    ncmp.size[1] + (2 * lvpwell_enc_ncmp),
                ),
                layer=layer["lvpwell"],
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
                layer=layer["dnwell"],
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
                    layer=layer["comp"],
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
                    layer=layer["comp"],
                )
            )
            rect_pcmpgr_out.move((rect_pcmpgr_in.xmin - cw, rect_pcmpgr_in.ymin - cw))
            B = c.add_ref(
                gf.geometry.boolean(
                    A=rect_pcmpgr_out,
                    B=rect_pcmpgr_in,
                    operation="A-B",
                    layer=layer["comp"],
                )
            )

            psdm_in = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) - 2 * pp_enc_comp,
                        (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) - 2 * pp_enc_comp,
                    ),
                    layer=layer["pplus"],
                )
            )
            psdm_in.move(
                (rect_pcmpgr_in.xmin + pp_enc_comp, rect_pcmpgr_in.ymin + pp_enc_comp,)
            )
            psdm_out = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (rect_pcmpgr_out.xmax - rect_pcmpgr_out.xmin) + 2 * pp_enc_comp,
                        (rect_pcmpgr_out.ymax - rect_pcmpgr_out.ymin) + 2 * pp_enc_comp,
                    ),
                    layer=layer["pplus"],
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
                    A=psdm_out, B=psdm_in, operation="A-B", layer=layer["pplus"]
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
                    via_layer=layer["contact"],
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
                    via_layer=layer["contact"],
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
                    via_layer=layer["contact"],
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
                    via_layer=layer["contact"],
                    via_size=(con_size, con_size),
                    via_spacing=(con_sp, con_sp),
                )
            )

            comp_m1_in = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(rect_pcmpgr_in.size[0], rect_pcmpgr_in.size[1]),
                    layer=layer["metal1"],
                )
            )

            comp_m1_out = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * cw,
                        (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * cw,
                    ),
                    layer=layer["metal1"],
                )
            )
            comp_m1_out.move((rect_pcmpgr_in.xmin - cw, rect_pcmpgr_in.ymin - cw))
            m1 = c.add_ref(
                gf.geometry.boolean(
                    A=rect_pcmpgr_out,
                    B=rect_pcmpgr_in,
                    operation="A-B",
                    layer=layer["metal1"],
                )
            )

    # creating layout and cell in klayout

    c.write_gds("diode_nd2ps_temp.gds")
    layout.read("diode_nd2ps_temp.gds")
    cell_name = "diode_nd2ps_dev"

    return layout.cell(cell_name)


def draw_diode_pd2nw(
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
     used to draw 3.3V P+/Nwell diode (Outside DNWELL) by specifying parameters
    Arguments:-
     layout     : Object of layout
     l          : Float of diffusion length
     w          : Float of diffusion width
     volt       : String of operating voltage of the diode [3.3V, 5V/6V]
     deepnwell  : Boolean of using Deep NWELL device
     pcmpgr     : Boolean of using P+ Guard Ring for Deep NWELL devices only
    """

    c = gf.Component("diode_pd2nw_dev")

    comp_spacing: float = 0.48
    np_enc_comp: float = 0.16
    pp_enc_comp: float = 0.16

    con_size = 0.22
    con_sp = 0.28
    con_comp_enc = 0.07

    dg_enc_cmp = 0.24
    dn_enc_nwell = 0.5
    nwell_ncmp_enc = 0.12
    nwell_pcmp_enc = 0.43
    pcmpgr_enc_dn = 2.5

    # p generation
    pcmp = c.add_ref(gf.components.rectangle(size=(w, l), layer=layer["comp"]))
    pplus = c.add_ref(
        gf.components.rectangle(
            size=(pcmp.size[0] + (2 * pp_enc_comp), pcmp.size[1] + (2 * pp_enc_comp),),
            layer=layer["pplus"],
        )
    )
    pplus.xmin = pcmp.xmin - pp_enc_comp
    pplus.ymin = pcmp.ymin - pp_enc_comp
    diode_mk = c.add_ref(
        gf.components.rectangle(
            size=(pcmp.size[0], pcmp.size[1]), layer=layer["diode_mk"]
        )
    )
    diode_mk.xmin = pcmp.xmin
    diode_mk.ymin = pcmp.ymin

    pcmp_con = c.add_ref(
        via_stack(
            x_range=(pcmp.xmin, pcmp.xmax),
            y_range=(pcmp.ymin, pcmp.ymax),
            base_layer=layer["comp"],
            metal_level=1,
        )
    )

    # p generation
    ncmp = c.add_ref(gf.components.rectangle(size=(cw, l), layer=layer["comp"]))
    ncmp.xmax = pcmp.xmin - comp_spacing
    nplus = c.add_ref(
        gf.components.rectangle(
            size=(ncmp.size[0] + (2 * np_enc_comp), ncmp.size[1] + (2 * np_enc_comp),),
            layer=layer["nplus"],
        )
    )
    nplus.xmin = ncmp.xmin - np_enc_comp
    nplus.ymin = ncmp.ymin - np_enc_comp

    ncmp_con = c.add_ref(
        via_stack(
            x_range=(ncmp.xmin, ncmp.xmax),
            y_range=(ncmp.ymin, ncmp.ymax),
            base_layer=layer["comp"],
            metal_level=1,
        )
    )

    if volt == "5/6V":
        dg = c.add_ref(
            gf.components.rectangle(
                size=(
                    pcmp.xmax - ncmp.xmin + (2 * dg_enc_cmp),
                    ncmp.size[1] + (2 * dg_enc_cmp),
                ),
                layer=layer["dualgate"],
            )
        )
        dg.xmin = ncmp.xmin - dg_enc_cmp
        dg.ymin = ncmp.ymin - dg_enc_cmp

    # nwell generation
    nwell = c.add_ref(
        gf.components.rectangle(
            size=(
                pcmp.xmax - ncmp.xmin + (nwell_ncmp_enc + nwell_pcmp_enc),
                pcmp.size[1] + (2 * nwell_pcmp_enc),
            ),
            layer=layer["nwell"],
        )
    )

    nwell.xmin = ncmp.xmin - nwell_ncmp_enc
    nwell.ymin = pcmp.ymin - nwell_pcmp_enc

    if deepnwell == 1:

        dn_rect = c.add_ref(
            gf.components.rectangle(
                size=(
                    nwell.size[0] + (2 * dn_enc_nwell),
                    nwell.size[1] + (2 * dn_enc_nwell),
                ),
                layer=layer["dnwell"],
            )
        )

        dn_rect.xmin = nwell.xmin - dn_enc_nwell
        dn_rect.ymin = nwell.ymin - dn_enc_nwell

        if pcmpgr == 1:

            c_temp_gr = gf.Component("temp_store guard ring")
            rect_pcmpgr_in = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (dn_rect.xmax - dn_rect.xmin) + 2 * pcmpgr_enc_dn,
                        (dn_rect.ymax - dn_rect.ymin) + 2 * pcmpgr_enc_dn,
                    ),
                    layer=layer["comp"],
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
                    layer=layer["comp"],
                )
            )
            rect_pcmpgr_out.move((rect_pcmpgr_in.xmin - cw, rect_pcmpgr_in.ymin - cw))
            B = c.add_ref(
                gf.geometry.boolean(
                    A=rect_pcmpgr_out,
                    B=rect_pcmpgr_in,
                    operation="A-B",
                    layer=layer["comp"],
                )
            )

            psdm_in = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) - 2 * pp_enc_comp,
                        (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) - 2 * pp_enc_comp,
                    ),
                    layer=layer["pplus"],
                )
            )
            psdm_in.move(
                (rect_pcmpgr_in.xmin + pp_enc_comp, rect_pcmpgr_in.ymin + pp_enc_comp,)
            )
            psdm_out = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (rect_pcmpgr_out.xmax - rect_pcmpgr_out.xmin) + 2 * pp_enc_comp,
                        (rect_pcmpgr_out.ymax - rect_pcmpgr_out.ymin) + 2 * pp_enc_comp,
                    ),
                    layer=layer["pplus"],
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
                    A=psdm_out, B=psdm_in, operation="A-B", layer=layer["pplus"]
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
                    via_layer=layer["contact"],
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
                    via_layer=layer["contact"],
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
                    via_layer=layer["contact"],
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
                    via_layer=layer["contact"],
                    via_size=(con_size, con_size),
                    via_spacing=(con_sp, con_sp),
                )
            )

            comp_m1_in = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(rect_pcmpgr_in.size[0], rect_pcmpgr_in.size[1]),
                    layer=layer["metal1"],
                )
            )

            comp_m1_out = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * cw,
                        (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * cw,
                    ),
                    layer=layer["metal1"],
                )
            )
            comp_m1_out.move((rect_pcmpgr_in.xmin - cw, rect_pcmpgr_in.ymin - cw))
            m1 = c.add_ref(
                gf.geometry.boolean(
                    A=rect_pcmpgr_out,
                    B=rect_pcmpgr_in,
                    operation="A-B",
                    layer=layer["metal1"],
                )
            )

    # creating layout and cell in klayout

    c.write_gds("diode_pd2nw_temp.gds")
    layout.read("diode_pd2nw_temp.gds")
    cell_name = "diode_pd2nw_dev"

    return layout.cell(cell_name)


def draw_diode_nw2ps(
    layout, l: float = 0.1, w: float = 0.1, cw: float = 0.1, volt: str = "3.3V"
) -> gf.Component:
    """
    Usage:-
     used to draw 3.3V Nwell/Psub diode by specifying parameters
    Arguments:-
     layout     : Object of layout
     l          : Float of diff length
     w          : Float of diff width
     cw         : Float of Cathode width
     volt       : String of operating voltage of the diode [3.3V, 5V/6V]
    """

    c = gf.Component("diode_nw2ps_dev")

    comp_spacing: float = 0.48
    np_enc_comp: float = 0.16
    pp_enc_comp: float = 0.16

    dg_enc_cmp = 0.24

    nwell_ncmp_enc = 0.16

    # n generation
    ncmp = c.add_ref(gf.components.rectangle(size=(w, l), layer=layer["comp"]))
    nplus = c.add_ref(
        gf.components.rectangle(
            size=(ncmp.size[0] + (2 * np_enc_comp), ncmp.size[1] + (2 * np_enc_comp),),
            layer=layer["nplus"],
        )
    )
    nplus.xmin = ncmp.xmin - np_enc_comp
    nplus.ymin = ncmp.ymin - np_enc_comp
    diode_mk = c.add_ref(
        gf.components.rectangle(
            size=(ncmp.size[0], ncmp.size[1]), layer=layer["diode_mk"]
        )
    )
    diode_mk.xmin = ncmp.xmin
    diode_mk.ymin = ncmp.ymin

    nwell = c.add_ref(
        gf.components.rectangle(
            size=(
                ncmp.size[0] + (2 * nwell_ncmp_enc),
                ncmp.size[1] + (2 * nwell_ncmp_enc),
            ),
            layer=layer["nwell"],
        )
    )
    nwell.xmin = ncmp.xmin - nwell_ncmp_enc
    nwell.ymin = ncmp.ymin - nwell_ncmp_enc

    ncmp_con = c.add_ref(
        via_stack(
            x_range=(ncmp.xmin, ncmp.xmax),
            y_range=(ncmp.ymin, ncmp.ymax),
            base_layer=layer["comp"],
            metal_level=1,
        )
    )

    # p generation
    pcmp = c.add_ref(gf.components.rectangle(size=(cw, l), layer=layer["comp"]))
    pcmp.xmax = ncmp.xmin - comp_spacing
    pplus = c.add_ref(
        gf.components.rectangle(
            size=(pcmp.size[0] + (2 * pp_enc_comp), pcmp.size[1] + (2 * pp_enc_comp),),
            layer=layer["pplus"],
        )
    )
    pplus.xmin = pcmp.xmin - pp_enc_comp
    pplus.ymin = pcmp.ymin - pp_enc_comp

    pcmp_con = c.add_ref(
        via_stack(
            x_range=(pcmp.xmin, pcmp.xmax),
            y_range=(pcmp.ymin, pcmp.ymax),
            base_layer=layer["comp"],
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
                layer=layer["dualgate"],
            )
        )
        dg.xmin = pcmp.xmin - dg_enc_cmp
        dg.ymin = pcmp.ymin - dg_enc_cmp

    # creating layout and cell in klayout

    c.write_gds("diode_nw2ps_temp.gds")
    layout.read("diode_nw2ps_temp.gds")
    cell_name = "diode_nw2ps_dev"

    return layout.cell(cell_name)


def draw_diode_pw2dw(
    layout,
    l: float = 0.1,
    w: float = 0.1,
    cw: float = 0.1,
    volt: str = "3.3V",
    pcmpgr: bool = 0,
) -> gf.Component:
    """
    Usage:-
     used to draw LVPWELL/DNWELL diode by specifying parameters
    Arguments:-
     layout     : Object of layout
     l          : Float of diff length
     w          : Float of diff width
     cw         : Float of cathode width
     volt       : String of operating voltage of the diode [3.3V, 5V/6V]
    """

    c = gf.Component("diode_pw2dw_dev")

    comp_spacing: float = 0.48
    np_enc_comp: float = 0.16
    pp_enc_comp: float = 0.16

    dg_enc_dn = 0.5

    lvpwell_enc_pcmp = 0.16
    dn_enc_lvpwell = 2.5

    con_size = 0.22
    con_sp = 0.28
    con_comp_enc = 0.07

    pcmpgr_enc_dn = 2.5

    # p generation
    pcmp = c.add_ref(gf.components.rectangle(size=(w, l), layer=layer["comp"]))
    pplus = c.add_ref(
        gf.components.rectangle(
            size=(pcmp.size[0] + (2 * pp_enc_comp), pcmp.size[1] + (2 * pp_enc_comp),),
            layer=layer["pplus"],
        )
    )
    pplus.xmin = pcmp.xmin - pp_enc_comp
    pplus.ymin = pcmp.ymin - pp_enc_comp
    diode_mk = c.add_ref(
        gf.components.rectangle(
            size=(pcmp.size[0], pcmp.size[1]), layer=layer["diode_mk"]
        )
    )
    diode_mk.xmin = pcmp.xmin
    diode_mk.ymin = pcmp.ymin

    lvpwell = c.add_ref(
        gf.components.rectangle(
            size=(
                pcmp.size[0] + (2 * lvpwell_enc_pcmp),
                pcmp.size[1] + (2 * lvpwell_enc_pcmp),
            ),
            layer=layer["lvpwell"],
        )
    )
    lvpwell.xmin = pcmp.xmin - lvpwell_enc_pcmp
    lvpwell.ymin = pcmp.ymin - lvpwell_enc_pcmp

    pcmp_con = c.add_ref(
        via_stack(
            x_range=(pcmp.xmin, pcmp.xmax),
            y_range=(pcmp.ymin, pcmp.ymax),
            base_layer=layer["comp"],
            metal_level=1,
        )
    )

    # p generation
    ncmp = c.add_ref(gf.components.rectangle(size=(cw, l), layer=layer["comp"]))
    ncmp.xmax = pcmp.xmin - comp_spacing
    nplus = c.add_ref(
        gf.components.rectangle(
            size=(ncmp.size[0] + (2 * np_enc_comp), ncmp.size[1] + (2 * np_enc_comp),),
            layer=layer["nplus"],
        )
    )
    nplus.xmin = ncmp.xmin - np_enc_comp
    nplus.ymin = ncmp.ymin - np_enc_comp

    ncmp_con = c.add_ref(
        via_stack(
            x_range=(ncmp.xmin, ncmp.xmax),
            y_range=(ncmp.ymin, ncmp.ymax),
            base_layer=layer["comp"],
            metal_level=1,
        )
    )

    dn_rect = c.add_ref(
        gf.components.rectangle(
            size=(
                lvpwell.size[0] + (2 * dn_enc_lvpwell),
                lvpwell.size[1] + (2 * dn_enc_lvpwell),
            ),
            layer=layer["dnwell"],
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
                layer=layer["comp"],
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
                layer=layer["comp"],
            )
        )
        rect_pcmpgr_out.move((rect_pcmpgr_in.xmin - cw, rect_pcmpgr_in.ymin - cw))
        B = c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["comp"],
            )
        )

        psdm_in = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) - 2 * pp_enc_comp,
                    (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) - 2 * pp_enc_comp,
                ),
                layer=layer["pplus"],
            )
        )
        psdm_in.move(
            (rect_pcmpgr_in.xmin + pp_enc_comp, rect_pcmpgr_in.ymin + pp_enc_comp,)
        )
        psdm_out = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (rect_pcmpgr_out.xmax - rect_pcmpgr_out.xmin) + 2 * pp_enc_comp,
                    (rect_pcmpgr_out.ymax - rect_pcmpgr_out.ymin) + 2 * pp_enc_comp,
                ),
                layer=layer["pplus"],
            )
        )
        psdm_out.move(
            (rect_pcmpgr_out.xmin - pp_enc_comp, rect_pcmpgr_out.ymin - pp_enc_comp,)
        )
        psdm = c.add_ref(
            gf.geometry.boolean(
                A=psdm_out, B=psdm_in, operation="A-B", layer=layer["pplus"]
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
                via_layer=layer["contact"],
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
                via_layer=layer["contact"],
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
                via_layer=layer["contact"],
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
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )

        comp_m1_in = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(rect_pcmpgr_in.size[0], rect_pcmpgr_in.size[1]),
                layer=layer["metal1"],
            )
        )

        comp_m1_out = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * cw,
                    (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * cw,
                ),
                layer=layer["metal1"],
            )
        )
        comp_m1_out.move((rect_pcmpgr_in.xmin - cw, rect_pcmpgr_in.ymin - cw))
        m1 = c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["metal1"],
            )
        )

    if volt == "5/6V":
        dg = c.add_ref(
            gf.components.rectangle(
                size=(
                    dn_rect.size[0] + (2 * dg_enc_dn),
                    dn_rect.size[1] + (2 * dg_enc_dn),
                ),
                layer=layer["dualgate"],
            )
        )
        dg.xmin = dn_rect.xmin - dg_enc_dn
        dg.ymin = dn_rect.ymin - dg_enc_dn

    # creating layout and cell in klayout

    c.write_gds("diode_pw2dw_temp.gds")
    layout.read("diode_pw2dw_temp.gds")
    cell_name = "diode_pw2dw_dev"

    return layout.cell(cell_name)


def draw_diode_dw2ps(
    layout,
    l: float = 0.1,
    w: float = 0.1,
    cw: float = 0.1,
    volt: str = "3.3V",
    pcmpgr: bool = 0,
) -> gf.Component:
    """
    Usage:-
     used to draw LVPWELL/DNWELL diode by specifying parameters
    Arguments:-
     layout     : Object of layout
     l          : Float of diff length
     w          : Float of diff width
     volt       : String of operating voltage of the diode [3.3V, 5V/6V]
    """

    c = gf.Component("diode_dw2ps_dev")

    if volt == "5/6V":
        dn_enc_ncmp = 0.66
    else:
        dn_enc_ncmp = 0.62

    comp_spacing = 0.32
    np_enc_comp: float = 0.16
    pp_enc_comp: float = 0.16

    con_size = 0.22
    con_sp = 0.28
    con_comp_enc = 0.07

    dg_enc_dn = 0.5

    pcmpgr_enc_dn = 2.5

    if (w < ((2 * cw) + comp_spacing)) or (l < ((2 * cw) + comp_spacing)):
        ncmp = c.add_ref(gf.components.rectangle(size=(w, l), layer=layer["comp"]))

        ncmp_con = c.add_ref(
            via_stack(
                x_range=(ncmp.xmin, ncmp.xmax),
                y_range=(ncmp.ymin, ncmp.ymax),
                base_layer=layer["comp"],
                metal_level=1,
            )
        )

        nplus = c.add_ref(
            gf.components.rectangle(
                size=(
                    ncmp.size[0] + (2 * np_enc_comp),
                    ncmp.size[1] + (2 * np_enc_comp),
                ),
                layer=layer["nplus"],
            )
        )
        nplus.xmin = ncmp.xmin - np_enc_comp
        nplus.ymin = ncmp.ymin - np_enc_comp
    else:
        c_temp = gf.Component("temp_store guard ring")
        ncmp_in = c_temp.add_ref(
            gf.components.rectangle(
                size=(w - (2 * cw), l - (2 * cw)), layer=layer["comp"],
            )
        )
        ncmp_out = c_temp.add_ref(
            gf.components.rectangle(size=(w, l), layer=layer["comp"],)
        )
        ncmp_out.move((ncmp_in.xmin - cw, ncmp_in.ymin - cw))
        ncmp = c.add_ref(
            gf.geometry.boolean(
                A=ncmp_out, B=ncmp_in, operation="A-B", layer=layer["comp"],
            )
        )

        pplus_in = c_temp.add_ref(
            gf.components.rectangle(
                size=(
                    (ncmp_in.xmax - ncmp_in.xmin) - 2 * pp_enc_comp,
                    (ncmp_in.ymax - ncmp_in.ymin) - 2 * pp_enc_comp,
                ),
                layer=layer["pplus"],
            )
        )
        pplus_in.move((ncmp_in.xmin + pp_enc_comp, ncmp_in.ymin + pp_enc_comp,))
        pplus_out = c_temp.add_ref(
            gf.components.rectangle(
                size=(
                    (ncmp_out.xmax - ncmp_out.xmin) + 2 * pp_enc_comp,
                    (ncmp_out.ymax - ncmp_out.ymin) + 2 * pp_enc_comp,
                ),
                layer=layer["pplus"],
            )
        )
        pplus_out.move((ncmp_out.xmin - pp_enc_comp, ncmp_out.ymin - pp_enc_comp,))
        pplus = c.add_ref(
            gf.geometry.boolean(
                A=pplus_out, B=pplus_in, operation="A-B", layer=layer["pplus"]
            )
        )

        # generating contacts

        ring_con_bot = c.add_ref(
            via_generator(
                x_range=(ncmp_in.xmin + con_size, ncmp_in.xmax - con_size,),
                y_range=(ncmp_out.ymin, ncmp_in.ymin),
                via_enclosure=(con_comp_enc, con_comp_enc),
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )

        ring_con_up = c.add_ref(
            via_generator(
                x_range=(ncmp_in.xmin + con_size, ncmp_in.xmax - con_size,),
                y_range=(ncmp_in.ymax, ncmp_out.ymax),
                via_enclosure=(con_comp_enc, con_comp_enc),
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )

        ring_con_r = c.add_ref(
            via_generator(
                x_range=(ncmp_out.xmin, ncmp_in.xmin),
                y_range=(ncmp_in.ymin + con_size, ncmp_in.ymax - con_size,),
                via_enclosure=(con_comp_enc, con_comp_enc),
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )

        ring_con_l = c.add_ref(
            via_generator(
                x_range=(ncmp_in.xmax, ncmp_out.xmax),
                y_range=(ncmp_in.ymin + con_size, ncmp_in.ymax - con_size,),
                via_enclosure=(con_comp_enc, con_comp_enc),
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )

        comp_m1_in = c_temp.add_ref(
            gf.components.rectangle(
                size=(ncmp_in.size[0], ncmp_in.size[1]), layer=layer["metal1"],
            )
        )

        comp_m1_out = c_temp.add_ref(
            gf.components.rectangle(
                size=(
                    (ncmp_in.xmax - ncmp_in.xmin) + 2 * cw,
                    (ncmp_in.ymax - ncmp_in.ymin) + 2 * cw,
                ),
                layer=layer["metal1"],
            )
        )
        comp_m1_out.move((ncmp_in.xmin - cw, ncmp_in.ymin - cw))
        m1 = c.add_ref(
            gf.geometry.boolean(
                A=ncmp_out, B=ncmp_in, operation="A-B", layer=layer["metal1"],
            )
        )

    # generate dnwell

    dn_rect = c.add_ref(
        gf.components.rectangle(
            size=(ncmp.size[0] + (2 * dn_enc_ncmp), ncmp.size[1] + (2 * dn_enc_ncmp),),
            layer=layer["dnwell"],
        )
    )
    dn_rect.xmin = ncmp.xmin - dn_enc_ncmp
    dn_rect.ymin = ncmp.ymin - dn_enc_ncmp

    diode_mk = c.add_ref(
        gf.components.rectangle(
            size=(dn_rect.size[0], dn_rect.size[1]), layer=layer["diode_mk"]
        )
    )
    diode_mk.xmin = dn_rect.xmin
    diode_mk.ymin = dn_rect.ymin

    if pcmpgr == 1:

        c_temp_gr = gf.Component("temp_store guard ring")
        rect_pcmpgr_in = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (dn_rect.xmax - dn_rect.xmin) + 2 * pcmpgr_enc_dn,
                    (dn_rect.ymax - dn_rect.ymin) + 2 * pcmpgr_enc_dn,
                ),
                layer=layer["comp"],
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
                layer=layer["comp"],
            )
        )
        rect_pcmpgr_out.move((rect_pcmpgr_in.xmin - cw, rect_pcmpgr_in.ymin - cw))
        B = c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["comp"],
            )
        )

        psdm_in = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) - 2 * pp_enc_comp,
                    (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) - 2 * pp_enc_comp,
                ),
                layer=layer["pplus"],
            )
        )
        psdm_in.move(
            (rect_pcmpgr_in.xmin + pp_enc_comp, rect_pcmpgr_in.ymin + pp_enc_comp,)
        )
        psdm_out = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (rect_pcmpgr_out.xmax - rect_pcmpgr_out.xmin) + 2 * pp_enc_comp,
                    (rect_pcmpgr_out.ymax - rect_pcmpgr_out.ymin) + 2 * pp_enc_comp,
                ),
                layer=layer["pplus"],
            )
        )
        psdm_out.move(
            (rect_pcmpgr_out.xmin - pp_enc_comp, rect_pcmpgr_out.ymin - pp_enc_comp,)
        )
        psdm = c.add_ref(
            gf.geometry.boolean(
                A=psdm_out, B=psdm_in, operation="A-B", layer=layer["pplus"]
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
                via_layer=layer["contact"],
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
                via_layer=layer["contact"],
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
                via_layer=layer["contact"],
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
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )

        comp_m1_in = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(rect_pcmpgr_in.size[0], rect_pcmpgr_in.size[1]),
                layer=layer["metal1"],
            )
        )

        comp_m1_out = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * cw,
                    (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * cw,
                ),
                layer=layer["metal1"],
            )
        )
        comp_m1_out.move((rect_pcmpgr_in.xmin - cw, rect_pcmpgr_in.ymin - cw))
        m1 = c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["metal1"],
            )
        )

    # generate dualgate

    if volt == "5/6V":
        dg = c.add_ref(
            gf.components.rectangle(
                size=(
                    dn_rect.size[0] + (2 * dg_enc_dn),
                    dn_rect.size[1] + (2 * dg_enc_dn),
                ),
                layer=layer["dualgate"],
            )
        )
        dg.xmin = dn_rect.xmin - dg_enc_dn
        dg.ymin = dn_rect.ymin - dg_enc_dn

    # creating layout and cell in klayout

    c.write_gds("diode_dw2ps_temp.gds")
    layout.read("diode_dw2ps_temp.gds")
    cell_name = "diode_dw2ps_dev"

    return layout.cell(cell_name)


def draw_sc_diode(
    layout,
    l: float = 0.1,
    w: float = 0.1,
    cw: float = 0.1,
    m: int = 1,
    pcmpgr: bool = 0,
) -> gf.Component:
    """
    Usage:-
     used to draw N+/LVPWELL diode (Outside DNWELL) by specifying parameters
    Arguments:-
     layout     : Object of layout
     l          : Float of diff length
     w          : Float of diff width
     m          : Integer of number of fingers
     pcmpgr     : Boolean of using P+ Guard Ring for Deep NWELL devices only
    """

    c = gf.Component("sc_diode_dev")

    sc_enc_comp = 0.16
    sc_comp_spacing = 0.28
    dn_enc_sc_an = 1.4
    np_enc_comp = 0.03
    m1_w = 0.23
    pcmpgr_enc_dn = 2.5
    pp_enc_comp: float = 0.16

    con_size = 0.22
    con_sp = 0.28
    con_comp_enc = 0.07

    # cathode draw

    @gf.cell
    def sc_cathode_strap(size: Float2 = (0.1, 0.1)) -> gf.Component:
        """Returns sc_diode cathode array element

        Args :
            size : size of cathode array element
        """

        c = gf.Component()

        ncmp = c.add_ref(gf.components.rectangle(size=size, layer=layer["comp"]))

        nplus = c.add_ref(
            gf.components.rectangle(
                size=(
                    ncmp.size[0] + (2 * np_enc_comp),
                    ncmp.size[1] + (2 * np_enc_comp),
                ),
                layer=layer["nplus"],
            )
        )
        nplus.xmin = ncmp.xmin - np_enc_comp
        nplus.ymin = ncmp.ymin - np_enc_comp

        ncmp_con = c.add_ref(
            via_stack(
                x_range=(ncmp.xmin, ncmp.xmax),
                y_range=(ncmp.ymin, ncmp.ymax),
                base_layer=layer["comp"],
                metal_level=1,
            )
        )

        return c

    @gf.cell
    def sc_anode_strap(size: Float2 = (0.1, 0.1)) -> gf.Component:
        """Returns sc_diode anode array element

        Args :
            size : size of anode array element
        """

        c = gf.Component()

        cmp = c.add_ref(gf.components.rectangle(size=size, layer=layer["comp"]))

        cmp_con = c.add_ref(
            via_stack(
                x_range=(cmp.xmin, cmp.xmax),
                y_range=(cmp.ymin, cmp.ymax),
                base_layer=layer["comp"],
                metal_level=1,
            )
        )

        return c

    sc_an = sc_anode_strap(size=(w, l))
    sc_cath = sc_cathode_strap(size=(cw, l))

    sc_cathode = c.add_array(
        component=sc_cath,
        rows=1,
        columns=(m + 1),
        spacing=((cw + w + (2 * sc_comp_spacing)), 0),
    )

    cath_m1_polys = sc_cath.get_polygons(by_spec=layer["metal1"])
    cath_m1_xmin = np.min(cath_m1_polys[0][:, 0])
    cath_m1_ymin = np.min(cath_m1_polys[0][:, 1])
    cath_m1_xmax = np.max(cath_m1_polys[0][:, 0])

    cath_m1_v = c.add_array(
        component=gf.components.rectangle(
            size=(cath_m1_xmax - cath_m1_xmin, cath_m1_ymin - sc_cathode.ymin + m1_w,),
            layer=layer["metal1"],
        ),
        rows=1,
        columns=(m + 1),
        spacing=((cw + w + (2 * sc_comp_spacing)), 0),
    )

    cath_m1_v.xmin = cath_m1_xmin
    cath_m1_v.ymax = cath_m1_ymin

    cath_m1_h = c.add_ref(
        gf.components.rectangle(size=(cath_m1_v.size[0], m1_w), layer=layer["metal1"])
    )
    cath_m1_h.xmin = cath_m1_v.xmin
    cath_m1_h.ymax = cath_m1_v.ymin

    sc_anode = c.add_array(
        component=sc_an, rows=1, columns=m, spacing=(w + cw + (2 * sc_comp_spacing), 0),
    )

    sc_anode.xmin = sc_cathode.xmin + (cw + sc_comp_spacing)

    if m > 1:
        an_m1_polys = sc_anode.get_polygons(by_spec=layer["metal1"])
        an_m1_xmin = np.min(an_m1_polys[0][:, 0])
        an_m1_xmax = np.max(an_m1_polys[0][:, 0])
        an_m1_ymax = np.max(an_m1_polys[0][:, 1])

        an_m1_v = c.add_array(
            component=gf.components.rectangle(
                size=(an_m1_xmax - an_m1_xmin, cath_m1_ymin - sc_an.ymin + m1_w,),
                layer=layer["metal1"],
            ),
            rows=1,
            columns=m,
            spacing=((cw + w + (2 * sc_comp_spacing)), 0),
        )

        an_m1_v.xmin = an_m1_xmin
        an_m1_v.ymin = an_m1_ymax

        an_m1_h = c.add_ref(
            gf.components.rectangle(size=(an_m1_v.size[0], m1_w), layer=layer["metal1"])
        )
        an_m1_h.xmin = an_m1_v.xmin
        an_m1_h.ymin = an_m1_v.ymax

    # diode_mk
    diode_mk = c.add_ref(
        gf.components.rectangle(
            size=(
                sc_cathode.size[0] + (2 * sc_enc_comp),
                sc_cathode.size[1] + (2 * sc_enc_comp),
            ),
            layer=layer["schottky_diode"],
        )
    )
    diode_mk.xmin = sc_cathode.xmin - sc_enc_comp
    diode_mk.ymin = sc_cathode.ymin - sc_enc_comp

    # dnwell
    dn_rect = c.add_ref(
        gf.components.rectangle(
            size=(
                sc_anode.size[0] + (2 * dn_enc_sc_an),
                sc_anode.size[1] + (2 * dn_enc_sc_an),
            ),
            layer=layer["dnwell"],
        )
    )
    dn_rect.xmin = sc_anode.xmin - dn_enc_sc_an
    dn_rect.ymin = sc_anode.ymin - dn_enc_sc_an

    if pcmpgr == 1:

        c_temp_gr = gf.Component("temp_store guard ring")
        rect_pcmpgr_in = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (dn_rect.xmax - dn_rect.xmin) + 2 * pcmpgr_enc_dn,
                    (dn_rect.ymax - dn_rect.ymin) + 2 * pcmpgr_enc_dn,
                ),
                layer=layer["comp"],
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
                layer=layer["comp"],
            )
        )
        rect_pcmpgr_out.move((rect_pcmpgr_in.xmin - cw, rect_pcmpgr_in.ymin - cw))
        B = c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["comp"],
            )
        )

        psdm_in = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) - 2 * pp_enc_comp,
                    (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) - 2 * pp_enc_comp,
                ),
                layer=layer["pplus"],
            )
        )
        psdm_in.move(
            (rect_pcmpgr_in.xmin + pp_enc_comp, rect_pcmpgr_in.ymin + pp_enc_comp,)
        )
        psdm_out = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (rect_pcmpgr_out.xmax - rect_pcmpgr_out.xmin) + 2 * pp_enc_comp,
                    (rect_pcmpgr_out.ymax - rect_pcmpgr_out.ymin) + 2 * pp_enc_comp,
                ),
                layer=layer["pplus"],
            )
        )
        psdm_out.move(
            (rect_pcmpgr_out.xmin - pp_enc_comp, rect_pcmpgr_out.ymin - pp_enc_comp,)
        )
        psdm = c.add_ref(
            gf.geometry.boolean(
                A=psdm_out, B=psdm_in, operation="A-B", layer=layer["pplus"]
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
                via_layer=layer["contact"],
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
                via_layer=layer["contact"],
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
                via_layer=layer["contact"],
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
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )

        comp_m1_in = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(rect_pcmpgr_in.size[0], rect_pcmpgr_in.size[1]),
                layer=layer["metal1"],
            )
        )

        comp_m1_out = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * cw,
                    (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * cw,
                ),
                layer=layer["metal1"],
            )
        )
        comp_m1_out.move((rect_pcmpgr_in.xmin - cw, rect_pcmpgr_in.ymin - cw))
        m1 = c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["metal1"],
            )
        )

    # creating layout and cell in klayout

    c.write_gds("sc_diode_temp.gds")
    layout.read("sc_diode_temp.gds")
    cell_name = "sc_diode_dev"

    return layout.cell(cell_name)
