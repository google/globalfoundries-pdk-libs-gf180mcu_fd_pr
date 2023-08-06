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
from gdsfactory.typings import Float2
from .via_generator import via_generator, via_stack

import numpy as np
import os


def draw_diode_nd2ps(
    layout,
    la: float = 0.1,
    wa: float = 0.1,
    cw: float = 0.1,
    volt: str = "3.3V",
    deepnwell: bool = 0,
    pcmpgr: bool = 0,
    lbl: bool = 0,
    p_lbl: str = "",
    n_lbl: str = "",
) -> gf.Component:

    """
    Usage:-
     used to draw N+/LVPWELL diode (Outside DNWELL) by specifying parameters
    Arguments:-
     layout     : Object of layout
     la         : Float of diff length (anode)
     wa         : Float of diff width (anode)
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
    lvpwell_enc_ncmp = 0.6 if (deepnwell == 1) else 0.16
    lvpwell_enc_pcmp = 0.16
    pcmpgr_enc_dn = 2.5
    dg_enc_dn = 0.5
    pcmp_gr_wid = 0.36

    # n generation
    ncmp = c.add_ref(gf.components.rectangle(size=(wa, la), layer=layer["comp"]))
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
    )  # ncomp_con

    # p generation
    pcmp = c.add_ref(gf.components.rectangle(size=(cw, la), layer=layer["comp"]))
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
    )  # pcomp_con

    # diode_mk
    diode_mk = c.add_ref(
        gf.components.rectangle(
            size=(nplus.xmax - pplus.xmin, nplus.size[1]), layer=layer["diode_mk"]
        )
    )
    diode_mk.xmin = pplus.xmin
    diode_mk.ymin = pplus.ymin

    # labels generation
    if lbl == 1:

        # n_label generation
        c.add_label(
            n_lbl,
            position=(
                ncmp_con.xmin + (ncmp_con.size[0] / 2),
                ncmp_con.ymin + (ncmp_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

        # p_label generation
        c.add_label(
            p_lbl,
            position=(
                pcmp_con.xmin + (pcmp_con.size[0] / 2),
                pcmp_con.ymin + (pcmp_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

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
            dg.center = dn_rect.center

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
                        (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * pcmp_gr_wid,
                        (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * pcmp_gr_wid,
                    ),
                    layer=layer["comp"],
                )
            )
            rect_pcmpgr_out.move(
                (rect_pcmpgr_in.xmin - pcmp_gr_wid, rect_pcmpgr_in.ymin - pcmp_gr_wid)
            )
            c.add_ref(
                gf.geometry.boolean(
                    A=rect_pcmpgr_out,
                    B=rect_pcmpgr_in,
                    operation="A-B",
                    layer=layer["comp"],
                )
            )  # guardring Bulk draw

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
            c.add_ref(
                gf.geometry.boolean(
                    A=psdm_out, B=psdm_in, operation="A-B", layer=layer["pplus"]
                )
            )  # psdm draw

            # generating contacts

            c.add_ref(
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
            )  # bottom contact

            c.add_ref(
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
            )  # upper contact

            c.add_ref(
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
            )  # right contact

            c.add_ref(
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
            )  # left contact

            comp_m1_in = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(rect_pcmpgr_in.size[0], rect_pcmpgr_in.size[1]),
                    layer=layer["metal1"],
                )
            )

            comp_m1_out = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (comp_m1_in.size[0]) + 2 * pcmp_gr_wid,
                        (comp_m1_in.size[1]) + 2 * pcmp_gr_wid,
                    ),
                    layer=layer["metal1"],
                )
            )
            comp_m1_out.move(
                (rect_pcmpgr_in.xmin - pcmp_gr_wid, rect_pcmpgr_in.ymin - pcmp_gr_wid)
            )
            c.add_ref(
                gf.geometry.boolean(
                    A=rect_pcmpgr_out,
                    B=rect_pcmpgr_in,
                    operation="A-B",
                    layer=layer["metal1"],
                )
            )  # guardring metal1

    else:

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

        lvpwell = c.add_ref(
            gf.components.rectangle(
                size=(diode_mk.size[0], diode_mk.size[1],), layer=layer["lvpwell"],
            )
        )

        lvpwell.center = diode_mk.center

    # creating layout and cell in klayout

    c.write_gds("diode_nd2ps_temp.gds")
    layout.read("diode_nd2ps_temp.gds")
    cell_name = "diode_nd2ps_dev"
    os.remove("diode_nd2ps_temp.gds")

    return layout.cell(cell_name)


def draw_diode_pd2nw(
    layout,
    la: float = 0.1,
    wa: float = 0.1,
    cw: float = 0.1,
    volt: str = "3.3V",
    deepnwell: bool = 0,
    pcmpgr: bool = 0,
    lbl: bool = 0,
    p_lbl: str = "",
    n_lbl: str = "",
) -> gf.Component:
    """
    Usage:-
     used to draw 3.3V P+/Nwell diode (Outside DNWELL) by specifying parameters
    Arguments:-
     layout     : Object of layout
     la         : Float of diffusion length (anode)
     wa         : Float of diffusion width (anode)
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
    nwell_ncmp_enc = 0.28
    nwell_pcmp_enc = 0.43 if volt == "3.3V" else 0.6
    pcmpgr_enc_dn = 2.5
    dg_enc_dn = 0.5
    pcmp_gr_wid = 0.36

    # p generation
    pcmp = c.add_ref(gf.components.rectangle(size=(wa, la), layer=layer["comp"]))
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
    )  # pcomp_contact

    # n generation
    ncmp = c.add_ref(gf.components.rectangle(size=(cw, la), layer=layer["comp"]))
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
    )  # ncomp contact

    # labels generation
    if lbl == 1:

        # n_label generation
        c.add_label(
            n_lbl,
            position=(
                ncmp_con.xmin + (ncmp_con.size[0] / 2),
                ncmp_con.ymin + (ncmp_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

        # p_label generation
        c.add_label(
            p_lbl,
            position=(
                pcmp_con.xmin + (pcmp_con.size[0] / 2),
                pcmp_con.ymin + (pcmp_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

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
            dg.center = dn_rect.center

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
                        (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * pcmp_gr_wid,
                        (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * pcmp_gr_wid,
                    ),
                    layer=layer["comp"],
                )
            )
            rect_pcmpgr_out.move(
                (rect_pcmpgr_in.xmin - pcmp_gr_wid, rect_pcmpgr_in.ymin - pcmp_gr_wid)
            )
            c.add_ref(
                gf.geometry.boolean(
                    A=rect_pcmpgr_out,
                    B=rect_pcmpgr_in,
                    operation="A-B",
                    layer=layer["comp"],
                )
            )  # Bulk guardring

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
            c.add_ref(
                gf.geometry.boolean(
                    A=psdm_out, B=psdm_in, operation="A-B", layer=layer["pplus"]
                )
            )  # psdm guardring

            # generating contacts

            c.add_ref(
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
            )  # bottom contact

            c.add_ref(
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
            )  # upper contact

            c.add_ref(
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
            )  # right contact

            c.add_ref(
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
            )  # left contact

            comp_m1_in = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(rect_pcmpgr_in.size[0], rect_pcmpgr_in.size[1]),
                    layer=layer["metal1"],
                )
            )

            comp_m1_out = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (comp_m1_in.size[0]) + 2 * pcmp_gr_wid,
                        (comp_m1_in.size[1]) + 2 * pcmp_gr_wid,
                    ),
                    layer=layer["metal1"],
                )
            )
            comp_m1_out.move(
                (rect_pcmpgr_in.xmin - pcmp_gr_wid, rect_pcmpgr_in.ymin - pcmp_gr_wid)
            )
            c.add_ref(
                gf.geometry.boolean(
                    A=rect_pcmpgr_out,
                    B=rect_pcmpgr_in,
                    operation="A-B",
                    layer=layer["metal1"],
                )
            )  # guardring metal1

    else:

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

    # creating layout and cell in klayout

    c.write_gds("diode_pd2nw_temp.gds")
    layout.read("diode_pd2nw_temp.gds")
    cell_name = "diode_pd2nw_dev"
    os.remove("diode_pd2nw_temp.gds")

    return layout.cell(cell_name)


def draw_diode_nw2ps(
    layout,
    la: float = 0.1,
    wa: float = 0.1,
    cw: float = 0.1,
    volt: str = "3.3V",
    lbl: bool = 0,
    p_lbl: str = "",
    n_lbl: str = "",
) -> gf.Component:
    """
    Usage:-
     used to draw 3.3V Nwell/Psub diode by specifying parameters
    Arguments:-
     layout     : Object of layout
     la         : Float of diff length (anode)
     wa         : Float of diff width (anode)
     cw         : Float of Cathode width
     volt       : String of operating voltage of the diode [3.3V, 5V/6V]
    """

    c = gf.Component("diode_nw2ps_dev")

    comp_spacing: float = 0.48
    np_enc_comp: float = 0.16
    pp_enc_comp: float = 0.16

    dg_enc_cmp = 0.24

    nwell_ncmp_enc = 0.16

    nwell = c.add_ref(gf.components.rectangle(size=(wa, la,), layer=layer["nwell"],))

    # n generation
    ncmp = c.add_ref(
        gf.components.rectangle(
            size=(
                nwell.size[0] - (2 * nwell_ncmp_enc),
                nwell.size[1] - (2 * nwell_ncmp_enc),
            ),
            layer=layer["comp"],
        )
    )
    ncmp.center = nwell.center

    nplus = c.add_ref(
        gf.components.rectangle(
            size=(ncmp.size[0] + (2 * np_enc_comp), ncmp.size[1] + (2 * np_enc_comp),),
            layer=layer["nplus"],
        )
    )
    nplus.xmin = ncmp.xmin - np_enc_comp
    nplus.ymin = ncmp.ymin - np_enc_comp

    n_con = c.add_ref(
        via_stack(
            x_range=(ncmp.xmin, ncmp.xmax),
            y_range=(ncmp.ymin, ncmp.ymax),
            base_layer=layer["comp"],
            metal_level=1,
        )
    )  # ncomp contact

    # p generation
    pcmp = c.add_ref(
        gf.components.rectangle(size=(cw, ncmp.size[1]), layer=layer["comp"])
    )
    pcmp.center = ncmp.center
    pcmp.xmax = ncmp.xmin - comp_spacing
    pplus = c.add_ref(
        gf.components.rectangle(
            size=(pcmp.size[0] + (2 * pp_enc_comp), pcmp.size[1] + (2 * pp_enc_comp),),
            layer=layer["pplus"],
        )
    )
    pplus.xmin = pcmp.xmin - pp_enc_comp
    pplus.ymin = pcmp.ymin - pp_enc_comp

    p_con = c.add_ref(
        via_stack(
            x_range=(pcmp.xmin, pcmp.xmax),
            y_range=(pcmp.ymin, pcmp.ymax),
            base_layer=layer["comp"],
            metal_level=1,
        )
    )  # pcmop contact

    diode_mk = c.add_ref(
        gf.components.rectangle(
            size=(nwell.xmax - pplus.xmin, nwell.size[1]), layer=layer["well_diode_mk"]
        )
    )
    diode_mk.xmin = pplus.xmin
    diode_mk.ymin = nwell.ymin

    # labels generation
    if lbl == 1:

        # n_label generation
        c.add_label(
            n_lbl,
            position=(
                n_con.xmin + (n_con.size[0] / 2),
                n_con.ymin + (n_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

        # p_label generation
        c.add_label(
            p_lbl,
            position=(
                p_con.xmin + (p_con.size[0] / 2),
                p_con.ymin + (p_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
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
    os.remove("diode_nw2ps_temp.gds")

    return layout.cell(cell_name)


def draw_diode_pw2dw(
    layout,
    la: float = 0.1,
    wa: float = 0.1,
    cw: float = 0.1,
    volt: str = "3.3V",
    pcmpgr: bool = 0,
    lbl: bool = 0,
    p_lbl: str = "",
    n_lbl: str = "",
) -> gf.Component:
    """
    Usage:-
     used to draw LVPWELL/DNWELL diode by specifying parameters
    Arguments:-
     layout     : Object of layout
     la         : Float of diff length (anode)
     wa         : Float of diff width (anode)
     cw         : Float of cathode width
     volt       : String of operating voltage of the diode [3.3V, 5V/6V]
    """

    c = gf.Component("diode_pw2dw_dev")

    comp_spacing: float = 0.92
    np_enc_comp: float = 0.16
    pp_enc_comp: float = 0.16

    dg_enc_dn = 0.5

    lvpwell_enc_pcmp = 0.16
    dn_enc_lvpwell = 2.5

    con_size = 0.22
    con_sp = 0.28
    con_comp_enc = 0.07

    pcmpgr_enc_dn = 2.5
    pcmp_gr_wid = 0.36
    grw = 0.36

    lvpwell = c.add_ref(
        gf.components.rectangle(size=(wa, la,), layer=layer["lvpwell"],)
    )

    diode_mk = c.add_ref(
        gf.components.rectangle(
            size=(lvpwell.size[0], lvpwell.size[1]), layer=layer["well_diode_mk"]
        )
    )
    diode_mk.xmin = lvpwell.xmin
    diode_mk.ymin = lvpwell.ymin

    if (wa < ((2 * grw) + comp_spacing + (2 * lvpwell_enc_pcmp))) or (
        la < ((2 * grw) + comp_spacing + (2 * lvpwell_enc_pcmp))
    ):

        # p generation
        pcmp = c.add_ref(
            gf.components.rectangle(
                size=(
                    lvpwell.size[0] - (2 * lvpwell_enc_pcmp),
                    lvpwell.size[1] - (2 * lvpwell_enc_pcmp),
                ),
                layer=layer["comp"],
            )
        )
        pcmp.center = lvpwell.center

        pplus = c.add_ref(
            gf.components.rectangle(
                size=(
                    pcmp.size[0] + (2 * pp_enc_comp),
                    pcmp.size[1] + (2 * pp_enc_comp),
                ),
                layer=layer["pplus"],
            )
        )
        pplus.xmin = pcmp.xmin - pp_enc_comp
        pplus.ymin = pcmp.ymin - pp_enc_comp

        p_con = c.add_ref(
            via_stack(
                x_range=(pcmp.xmin, pcmp.xmax),
                y_range=(pcmp.ymin, pcmp.ymax),
                base_layer=layer["comp"],
                metal_level=1,
            )
        )  # pcomp_contact

    else:

        c_temp = gf.Component("temp_store guard ring")

        pcmp_in = c_temp.add_ref(
            gf.components.rectangle(
                size=(
                    lvpwell.size[0] - (2 * lvpwell_enc_pcmp) - (2 * grw),
                    lvpwell.size[1] - (2 * lvpwell_enc_pcmp) - (2 * grw),
                ),
                layer=layer["comp"],
            )
        )
        pcmp_in.center = lvpwell.center

        pcmp_out = c_temp.add_ref(
            gf.components.rectangle(
                size=(
                    lvpwell.size[0] - (2 * lvpwell_enc_pcmp),
                    lvpwell.size[1] - (2 * lvpwell_enc_pcmp),
                ),
                layer=layer["comp"],
            )
        )
        pcmp_out.move((pcmp_in.xmin - grw, pcmp_in.ymin - grw))
        pcmp = c.add_ref(
            gf.geometry.boolean(
                A=pcmp_out, B=pcmp_in, operation="A-B", layer=layer["comp"],
            )
        )

        pplus_in = c_temp.add_ref(
            gf.components.rectangle(
                size=(
                    (pcmp_in.xmax - pcmp_in.xmin) - 2 * pp_enc_comp,
                    (pcmp_in.ymax - pcmp_in.ymin) - 2 * pp_enc_comp,
                ),
                layer=layer["pplus"],
            )
        )
        pplus_in.move((pcmp_in.xmin + pp_enc_comp, pcmp_in.ymin + pp_enc_comp,))
        pplus_out = c_temp.add_ref(
            gf.components.rectangle(
                size=(
                    (pcmp_out.xmax - pcmp_out.xmin) + 2 * pp_enc_comp,
                    (pcmp_out.ymax - pcmp_out.ymin) + 2 * pp_enc_comp,
                ),
                layer=layer["pplus"],
            )
        )
        pplus_out.move((pcmp_out.xmin - pp_enc_comp, pcmp_out.ymin - pp_enc_comp,))
        pplus = c.add_ref(
            gf.geometry.boolean(
                A=pplus_out, B=pplus_in, operation="A-B", layer=layer["pplus"]
            )
        )  # pplus

        # generating contacts

        c.add_ref(
            via_generator(
                x_range=(pcmp_in.xmin + con_size, pcmp_in.xmax - con_size,),
                y_range=(pcmp_out.ymin, pcmp_in.ymin),
                via_enclosure=(con_comp_enc, con_comp_enc),
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )  # bottom contact

        c.add_ref(
            via_generator(
                x_range=(pcmp_in.xmin + con_size, pcmp_in.xmax - con_size,),
                y_range=(pcmp_in.ymax, pcmp_out.ymax),
                via_enclosure=(con_comp_enc, con_comp_enc),
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )  # upper contact

        p_con = c.add_ref(
            via_generator(
                x_range=(pcmp_out.xmin, pcmp_in.xmin),
                y_range=(pcmp_in.ymin + con_size, pcmp_in.ymax - con_size,),
                via_enclosure=(con_comp_enc, con_comp_enc),
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )  # left contact

        c.add_ref(
            via_generator(
                x_range=(pcmp_in.xmax, pcmp_out.xmax),
                y_range=(pcmp_in.ymin + con_size, pcmp_in.ymax - con_size,),
                via_enclosure=(con_comp_enc, con_comp_enc),
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )  # right contact

        c.add_ref(
            gf.geometry.boolean(
                A=pcmp_out, B=pcmp_in, operation="A-B", layer=layer["metal1"],
            )
        )  # guardring metal1

    # n generation
    ncmp = c.add_ref(
        gf.components.rectangle(
            size=(cw, lvpwell.size[1] - (2 * lvpwell_enc_pcmp)), layer=layer["comp"]
        )
    )
    ncmp.center = pcmp.center
    ncmp.xmax = pcmp.xmin - comp_spacing

    nplus = c.add_ref(
        gf.components.rectangle(
            size=(ncmp.size[0] + (2 * np_enc_comp), ncmp.size[1] + (2 * np_enc_comp),),
            layer=layer["nplus"],
        )
    )
    nplus.xmin = ncmp.xmin - np_enc_comp
    nplus.ymin = ncmp.ymin - np_enc_comp

    n_con = c.add_ref(
        via_stack(
            x_range=(ncmp.xmin, ncmp.xmax),
            y_range=(ncmp.ymin, ncmp.ymax),
            base_layer=layer["comp"],
            metal_level=1,
        )
    )  # ncomp contact

    # labels generation
    if lbl == 1:

        # n_label generation
        c.add_label(
            n_lbl,
            position=(
                n_con.xmin + (n_con.size[0] / 2),
                n_con.ymin + (n_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

        # p_label generation
        c.add_label(
            p_lbl,
            position=(
                p_con.xmin + (p_con.size[0] / 2),
                p_con.ymin + (p_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

    dn_rect = c.add_ref(
        gf.components.rectangle(
            size=(
                lvpwell.xmax - nplus.xmin + (2 * dn_enc_lvpwell),
                lvpwell.size[1] + (2 * dn_enc_lvpwell),
            ),
            layer=layer["dnwell"],
        )
    )

    dn_rect.xmax = lvpwell.xmax + dn_enc_lvpwell
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
                    (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * pcmp_gr_wid,
                    (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * pcmp_gr_wid,
                ),
                layer=layer["comp"],
            )
        )
        rect_pcmpgr_out.move(
            (rect_pcmpgr_in.xmin - pcmp_gr_wid, rect_pcmpgr_in.ymin - pcmp_gr_wid)
        )
        c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["comp"],
            )
        )  # guardring Bulk

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
        c.add_ref(
            gf.geometry.boolean(
                A=psdm_out, B=psdm_in, operation="A-B", layer=layer["pplus"]
            )
        )  # guardring psdm

        # generating contacts

        c.add_ref(
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
        )  # bottom contact

        c.add_ref(
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
        )  # upper contact

        c.add_ref(
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
        )  # right contact

        c.add_ref(
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
        )  # left contact

        comp_m1_in = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(rect_pcmpgr_in.size[0], rect_pcmpgr_in.size[1]),
                layer=layer["metal1"],
            )
        )

        comp_m1_out = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (comp_m1_in.size[0]) + 2 * pcmp_gr_wid,
                    (comp_m1_in.size[1]) + 2 * pcmp_gr_wid,
                ),
                layer=layer["metal1"],
            )
        )
        comp_m1_out.move(
            (rect_pcmpgr_in.xmin - pcmp_gr_wid, rect_pcmpgr_in.ymin - pcmp_gr_wid)
        )
        c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["metal1"],
            )
        )  # guardring metal1

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
    os.remove("diode_pw2dw_temp.gds")

    return layout.cell(cell_name)


def draw_diode_dw2ps(
    layout,
    la: float = 0.1,
    wa: float = 0.1,
    cw: float = 0.1,
    volt: str = "3.3V",
    pcmpgr: bool = 0,
    lbl: bool = 0,
    p_lbl: str = "",
    n_lbl: str = "",
) -> gf.Component:
    """
    Usage:-
     used to draw LVPWELL/DNWELL diode by specifying parameters
    Arguments:-
     layout     : Object of layout
     la         : Float of diff length (anode)
     wa         : Float of diff width (anode)
     volt       : String of operating voltage of the diode [3.3V, 5V/6V]
    """

    c = gf.Component("diode_dw2ps_dev")

    if volt == "5/6V":
        dn_enc_ncmp = 0.66
    else:
        dn_enc_ncmp = 0.62

    comp_spacing = 0.92
    np_enc_comp: float = 0.16
    pp_enc_comp: float = 0.16

    con_size = 0.22
    con_sp = 0.28
    con_comp_enc = 0.07

    dg_enc_dn = 0.5

    pcmpgr_enc_dn = 2.5
    pcmp_gr_wid = 0.36

    dn_rect = c.add_ref(gf.components.rectangle(size=(wa, la), layer=layer["dnwell"],))

    diode_mk = c.add_ref(
        gf.components.rectangle(
            size=(dn_rect.size[0], dn_rect.size[1]), layer=layer["well_diode_mk"]
        )
    )
    diode_mk.xmin = dn_rect.xmin
    diode_mk.ymin = dn_rect.ymin

    if (wa < ((2 * cw) + comp_spacing + (2 * dn_enc_ncmp))) or (
        la < ((2 * cw) + comp_spacing + (2 * dn_enc_ncmp))
    ):
        ncmp = c.add_ref(
            gf.components.rectangle(
                size=(cw, la - (2 * dn_enc_ncmp)), layer=layer["comp"]
            )
        )
        ncmp.center = dn_rect.center

        n_con = c.add_ref(
            via_stack(
                x_range=(ncmp.xmin, ncmp.xmax),
                y_range=(ncmp.ymin, ncmp.ymax),
                base_layer=layer["comp"],
                metal_level=1,
            )
        )  # ncomp_contact

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
                size=(
                    wa - (2 * dn_enc_ncmp) - (2 * cw),
                    la - (2 * dn_enc_ncmp) - (2 * cw),
                ),
                layer=layer["comp"],
            )
        )
        ncmp_in.center = dn_rect.center
        ncmp_out = c_temp.add_ref(
            gf.components.rectangle(
                size=(wa - (2 * dn_enc_ncmp), la - (2 * dn_enc_ncmp)),
                layer=layer["comp"],
            )
        )
        ncmp_out.move((ncmp_in.xmin - cw, ncmp_in.ymin - cw))
        ncmp = c.add_ref(
            gf.geometry.boolean(
                A=ncmp_out, B=ncmp_in, operation="A-B", layer=layer["comp"],
            )
        )

        nplus_in = c_temp.add_ref(
            gf.components.rectangle(
                size=(
                    (ncmp_in.xmax - ncmp_in.xmin) - 2 * pp_enc_comp,
                    (ncmp_in.ymax - ncmp_in.ymin) - 2 * pp_enc_comp,
                ),
                layer=layer["pplus"],
            )
        )
        nplus_in.move((ncmp_in.xmin + pp_enc_comp, ncmp_in.ymin + pp_enc_comp,))
        nplus_out = c_temp.add_ref(
            gf.components.rectangle(
                size=(
                    (ncmp_out.xmax - ncmp_out.xmin) + 2 * pp_enc_comp,
                    (ncmp_out.ymax - ncmp_out.ymin) + 2 * pp_enc_comp,
                ),
                layer=layer["nplus"],
            )
        )
        nplus_out.move((ncmp_out.xmin - pp_enc_comp, ncmp_out.ymin - pp_enc_comp,))
        nplus = c.add_ref(
            gf.geometry.boolean(
                A=nplus_out, B=nplus_in, operation="A-B", layer=layer["nplus"]
            )
        )  # nplus

        # generating contacts

        c.add_ref(
            via_generator(
                x_range=(ncmp_in.xmin + con_size, ncmp_in.xmax - con_size,),
                y_range=(ncmp_out.ymin, ncmp_in.ymin),
                via_enclosure=(con_comp_enc, con_comp_enc),
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )  # bottom contact

        c.add_ref(
            via_generator(
                x_range=(ncmp_in.xmin + con_size, ncmp_in.xmax - con_size,),
                y_range=(ncmp_in.ymax, ncmp_out.ymax),
                via_enclosure=(con_comp_enc, con_comp_enc),
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )  # upper contact

        n_con = c.add_ref(
            via_generator(
                x_range=(ncmp_out.xmin, ncmp_in.xmin),
                y_range=(ncmp_in.ymin + con_size, ncmp_in.ymax - con_size,),
                via_enclosure=(con_comp_enc, con_comp_enc),
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )  # left contact

        c.add_ref(
            via_generator(
                x_range=(ncmp_in.xmax, ncmp_out.xmax),
                y_range=(ncmp_in.ymin + con_size, ncmp_in.ymax - con_size,),
                via_enclosure=(con_comp_enc, con_comp_enc),
                via_layer=layer["contact"],
                via_size=(con_size, con_size),
                via_spacing=(con_sp, con_sp),
            )
        )  # right contact

        comp_m1_in = c_temp.add_ref(
            gf.components.rectangle(
                size=(ncmp_in.size[0], ncmp_in.size[1]), layer=layer["metal1"],
            )
        )

        comp_m1_out = c_temp.add_ref(
            gf.components.rectangle(
                size=((comp_m1_in.size[0]) + 2 * cw, (comp_m1_in.size[0]) + 2 * cw,),
                layer=layer["metal1"],
            )
        )
        comp_m1_out.move((ncmp_in.xmin - cw, ncmp_in.ymin - cw))
        c.add_ref(
            gf.geometry.boolean(
                A=ncmp_out, B=ncmp_in, operation="A-B", layer=layer["metal1"],
            )
        )  # guardring metal1

    # labels generation
    if lbl == 1:

        # n_label generation
        c.add_label(
            n_lbl,
            position=(
                n_con.xmin + (n_con.size[0] / 2),
                n_con.ymin + (n_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

    # generate dnwell

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
                    (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * pcmp_gr_wid,
                    (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * pcmp_gr_wid,
                ),
                layer=layer["comp"],
            )
        )
        rect_pcmpgr_out.move(
            (rect_pcmpgr_in.xmin - pcmp_gr_wid, rect_pcmpgr_in.ymin - pcmp_gr_wid)
        )
        c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["comp"],
            )
        )  # guardring Bulk

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
        c.add_ref(
            gf.geometry.boolean(
                A=psdm_out, B=psdm_in, operation="A-B", layer=layer["pplus"]
            )
        )  # psdm

        # generating contacts

        c.add_ref(
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
        )  # bottom contact

        c.add_ref(
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
        )  # upper contact

        p_con = c.add_ref(
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
        )  # left contact

        c.add_ref(
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
        )  # right contact

        # labels generation
        if lbl == 1:

            # n_label generation
            c.add_label(
                p_lbl,
                position=(
                    p_con.xmin + (p_con.size[0] / 2),
                    p_con.ymin + (p_con.size[1] / 2),
                ),
                layer=layer["metal1_label"],
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
                    (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * pcmp_gr_wid,
                    (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * pcmp_gr_wid,
                ),
                layer=layer["metal1"],
            )
        )
        comp_m1_out.move(
            (rect_pcmpgr_in.xmin - pcmp_gr_wid, rect_pcmpgr_in.ymin - pcmp_gr_wid)
        )
        c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["metal1"],
            )
        )  # guardring metal1

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
    os.remove("diode_dw2ps_temp.gds")

    return layout.cell(cell_name)


def draw_sc_diode(
    layout,
    la: float = 0.1,
    wa: float = 0.1,
    cw: float = 0.1,
    m: int = 1,
    pcmpgr: bool = 0,
    lbl: bool = 0,
    p_lbl: str = "",
    n_lbl: str = "",
) -> gf.Component:
    """
    Usage:-
     used to draw N+/LVPWELL diode (Outside DNWELL) by specifying parameters
    Arguments:-
     layout     : Object of layout
     la         : Float of diff length (anode)
     wa         : Float of diff width (anode)
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
    pcmp_gr_wid = 0.36

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

        c.add_ref(
            via_stack(
                x_range=(ncmp.xmin, ncmp.xmax),
                y_range=(ncmp.ymin, ncmp.ymax),
                base_layer=layer["comp"],
                metal_level=1,
            )
        )  # ncomp contact

        return c

    @gf.cell
    def sc_anode_strap(size: Float2 = (0.1, 0.1)) -> gf.Component:
        """Returns sc_diode anode array element

        Args :
            size : size of anode array element
        """

        c = gf.Component()

        cmp = c.add_ref(gf.components.rectangle(size=size, layer=layer["comp"]))

        c.add_ref(
            via_stack(
                x_range=(cmp.xmin, cmp.xmax),
                y_range=(cmp.ymin, cmp.ymax),
                base_layer=layer["comp"],
                metal_level=1,
            )
        )  # comp contact

        return c

    sc_an = sc_anode_strap(size=(wa, la))
    sc_cath = sc_cathode_strap(size=(cw, la))

    sc_cathode = c.add_array(
        component=sc_cath,
        rows=1,
        columns=(m + 1),
        spacing=((cw + wa + (2 * sc_comp_spacing)), 0),
    )

    cath_m1_polys = sc_cath.get_polygons(by_spec=layer["metal1"])
    cath_m1_xmin = np.min(cath_m1_polys[0][:, 0])
    cath_m1_ymin = np.min(cath_m1_polys[0][:, 1])
    cath_m1_xmax = np.max(cath_m1_polys[0][:, 0])

    cath_m1_v = c.add_array(
        component=gf.components.rectangle(
            size=(
                cath_m1_xmax - cath_m1_xmin,
                cath_m1_ymin - sc_cathode.ymin + m1_w + 0.001,
            ),
            layer=layer["metal1"],
        ),
        rows=1,
        columns=(m + 1),
        spacing=((cw + wa + (2 * sc_comp_spacing)), 0),
    )

    cath_m1_v.xmin = cath_m1_xmin
    cath_m1_v.ymax = cath_m1_ymin + 0.001

    cath_m1_h = c.add_ref(
        gf.components.rectangle(size=(cath_m1_v.size[0], m1_w), layer=layer["metal1"])
    )
    cath_m1_h.xmin = cath_m1_v.xmin
    cath_m1_h.ymax = cath_m1_v.ymin

    # cathode label generation
    if lbl == 1:
        c.add_label(
            n_lbl,
            position=(
                cath_m1_h.xmin + (cath_m1_h.size[0] / 2),
                cath_m1_h.ymin + (cath_m1_h.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

    sc_anode = c.add_array(
        component=sc_an,
        rows=1,
        columns=m,
        spacing=(wa + cw + (2 * sc_comp_spacing), 0),
    )

    sc_anode.xmin = sc_cathode.xmin + (cw + sc_comp_spacing + np_enc_comp)

    an_m1_polys = sc_anode.get_polygons(by_spec=layer["metal1"])
    an_m1_xmin = np.min(an_m1_polys[0][:, 0])
    an_m1_ymin = np.min(an_m1_polys[0][:, 1])
    an_m1_xmax = np.max(an_m1_polys[0][:, 0])
    an_m1_ymax = np.max(an_m1_polys[0][:, 1])

    if m > 1:

        an_m1_v = c.add_array(
            component=gf.components.rectangle(
                size=(
                    an_m1_xmax - an_m1_xmin,
                    cath_m1_ymin - sc_an.ymin + m1_w + 0.001,
                ),
                layer=layer["metal1"],
            ),
            rows=1,
            columns=m,
            spacing=((cw + wa + (2 * sc_comp_spacing)), 0),
        )

        an_m1_v.xmin = an_m1_xmin
        an_m1_v.ymin = an_m1_ymax

        an_m1_h = c.add_ref(
            gf.components.rectangle(size=(an_m1_v.size[0], m1_w), layer=layer["metal1"])
        )
        an_m1_h.xmin = an_m1_v.xmin
        an_m1_h.ymin = an_m1_v.ymax - 0.001

        # anode label generation
        if lbl == 1:
            c.add_label(
                p_lbl,
                position=(
                    an_m1_h.xmin + (an_m1_h.size[0] / 2),
                    an_m1_h.ymin + (an_m1_h.size[1] / 2),
                ),
                layer=layer["metal1_label"],
            )

    else:

        # anode label generation
        if lbl == 1:
            c.add_label(
                p_lbl,
                position=(
                    an_m1_xmin + ((an_m1_xmax - an_m1_xmin) / 2),
                    an_m1_ymin + ((an_m1_ymax - an_m1_ymin) / 2),
                ),
                layer=layer["metal1_label"],
            )

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
                sc_cathode.size[0] + (2 * dn_enc_sc_an),
                sc_anode.size[1] + (2 * dn_enc_sc_an),
            ),
            layer=layer["dnwell"],
        )
    )
    dn_rect.xmin = sc_cathode.xmin - dn_enc_sc_an
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
                    (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * pcmp_gr_wid,
                    (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * pcmp_gr_wid,
                ),
                layer=layer["comp"],
            )
        )
        rect_pcmpgr_out.move(
            (rect_pcmpgr_in.xmin - pcmp_gr_wid, rect_pcmpgr_in.ymin - pcmp_gr_wid)
        )
        c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["comp"],
            )
        )  # guardring Bulk

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
        c.add_ref(
            gf.geometry.boolean(
                A=psdm_out, B=psdm_in, operation="A-B", layer=layer["pplus"]
            )
        )  # psdm

        # generating contacts

        c.add_ref(
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
        )  # bottom contact

        c.add_ref(
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
        )  # upper contact

        c.add_ref(
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
        )  # right contact

        c.add_ref(
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
        )  # left contact

        comp_m1_in = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(rect_pcmpgr_in.size[0], rect_pcmpgr_in.size[1]),
                layer=layer["metal1"],
            )
        )

        comp_m1_out = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (comp_m1_in.size[0]) + 2 * pcmp_gr_wid,
                    (comp_m1_in.size[1]) + 2 * pcmp_gr_wid,
                ),
                layer=layer["metal1"],
            )
        )
        comp_m1_out.move(
            (rect_pcmpgr_in.xmin - pcmp_gr_wid, rect_pcmpgr_in.ymin - pcmp_gr_wid)
        )
        c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["metal1"],
            )
        )  # guardring metal1

    # creating layout and cell in klayout

    c.write_gds("sc_diode_temp.gds")
    layout.read("sc_diode_temp.gds")
    cell_name = "sc_diode_dev"
    os.remove("sc_diode_temp.gds")

    return layout.cell(cell_name)
