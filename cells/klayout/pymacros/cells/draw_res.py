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
## Resistor Pcells Generators for Klayout of GF180MCU
########################################################################################################################

import gdsfactory as gf
from gdsfactory.typings import LayerSpec, Float2
from .layers_def import layer
from .via_generator import via_generator, via_stack
import os


def draw_metal_res(
    layout,
    l_res: float = 0.1,
    w_res: float = 0.1,
    res_type: str = "rm1",
    tm_level: str = "LM6",
    lbl: bool = 0,
    r0_lbl: str = "",
    r1_lbl: str = "",
) -> gf.Component:
    """
    Usage:-
     used to draw 2-terminal Metal resistor by specifying parameters
    Arguments:-
     layout : Object of layout
     l      : Float of diff length
     w      : Float of diff width
    """

    c = gf.Component("res_dev")

    m_ext = 0.28

    if res_type == "rm1":
        m_layer = layer["metal1"]
        res_layer = layer["metal1_res"]
        m_lbl_layer = layer["metal1_label"]
    elif res_type == "rm2":
        m_layer = layer["metal2"]
        res_layer = layer["metal2_res"]
        m_lbl_layer = layer["metal2_label"]
    elif res_type == "rm3":
        m_layer = layer["metal3"]
        res_layer = layer["metal3_res"]
        m_lbl_layer = layer["metal3_label"]
    else:

        if tm_level == "3LM":
            m_layer = layer["metal3"]
            res_layer = layer["metal3_res"]
            m_lbl_layer = layer["metal3_label"]
        elif tm_level == "4LM":
            m_layer = layer["metal4"]
            res_layer = layer["metal4_res"]
            m_lbl_layer = layer["metal4_label"]
        elif tm_level == "5LM":
            m_layer = layer["metal5"]
            res_layer = layer["metal5_res"]
            m_lbl_layer = layer["metal5_label"]
        else:
            m_layer = layer["metaltop"]
            res_layer = layer["metal6_res"]
            m_lbl_layer = layer["metaltop_label"]

    res_mk = c.add_ref(gf.components.rectangle(size=(l_res, w_res), layer=res_layer))

    m_rect = c.add_ref(
        gf.components.rectangle(size=(l_res + (2 * m_ext), w_res), layer=m_layer)
    )
    m_rect.xmin = res_mk.xmin - m_ext
    m_rect.ymin = res_mk.ymin

    # labels generation
    if lbl == 1:
        c.add_label(
            r0_lbl,
            position=(
                res_mk.xmin + (res_mk.size[0] / 2),
                res_mk.ymin + (res_mk.size[1] / 2),
            ),
            layer=m_lbl_layer,
        )
        c.add_label(
            r1_lbl,
            position=(
                m_rect.xmin + (res_mk.xmin - m_rect.xmin) / 2,
                m_rect.ymin + (m_rect.size[1] / 2),
            ),
            layer=m_lbl_layer,
        )

    # creating layout and cell in klayout
    c.write_gds("res_temp.gds")
    layout.read("res_temp.gds")
    cell_name = "res_dev"
    os.remove("res_temp.gds")

    return layout.cell(cell_name)


@gf.cell
def pcmpgr_gen(dn_rect, grw: float = 0.36) -> gf.Component:
    """Return deepnwell guardring

    Args :
        dn_rect : deepnwell polygon
        grw : guardring width
    """

    c = gf.Component()

    comp_pp_enc: float = 0.16
    con_size = 0.22
    con_sp = 0.28
    con_comp_enc = 0.07
    pcmpgr_enc_dn = 2.5

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
    rect_pcmpgr_in.move((dn_rect.xmin - pcmpgr_enc_dn, dn_rect.ymin - pcmpgr_enc_dn))
    rect_pcmpgr_out = c_temp_gr.add_ref(
        gf.components.rectangle(
            size=(
                (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * grw,
                (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * grw,
            ),
            layer=layer["comp"],
        )
    )
    rect_pcmpgr_out.move((rect_pcmpgr_in.xmin - grw, rect_pcmpgr_in.ymin - grw))
    c.add_ref(
        gf.geometry.boolean(
            A=rect_pcmpgr_out, B=rect_pcmpgr_in, operation="A-B", layer=layer["comp"],
        )
    )  # guardring bulk

    psdm_in = c_temp_gr.add_ref(
        gf.components.rectangle(
            size=(
                (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) - 2 * comp_pp_enc,
                (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) - 2 * comp_pp_enc,
            ),
            layer=layer["pplus"],
        )
    )
    psdm_in.move(
        (rect_pcmpgr_in.xmin + comp_pp_enc, rect_pcmpgr_in.ymin + comp_pp_enc,)
    )
    psdm_out = c_temp_gr.add_ref(
        gf.components.rectangle(
            size=(
                (rect_pcmpgr_out.xmax - rect_pcmpgr_out.xmin) + 2 * comp_pp_enc,
                (rect_pcmpgr_out.ymax - rect_pcmpgr_out.ymin) + 2 * comp_pp_enc,
            ),
            layer=layer["pplus"],
        )
    )
    psdm_out.move(
        (rect_pcmpgr_out.xmin - comp_pp_enc, rect_pcmpgr_out.ymin - comp_pp_enc,)
    )
    c.add_ref(
        gf.geometry.boolean(
            A=psdm_out, B=psdm_in, operation="A-B", layer=layer["pplus"]
        )
    )  # pplus_draw

    # generating contacts

    c.add_ref(
        via_generator(
            x_range=(rect_pcmpgr_in.xmin + con_size, rect_pcmpgr_in.xmax - con_size,),
            y_range=(rect_pcmpgr_out.ymin, rect_pcmpgr_in.ymin),
            via_enclosure=(con_comp_enc, con_comp_enc),
            via_layer=layer["contact"],
            via_size=(con_size, con_size),
            via_spacing=(con_sp, con_sp),
        )
    )  # bottom contact

    c.add_ref(
        via_generator(
            x_range=(rect_pcmpgr_in.xmin + con_size, rect_pcmpgr_in.xmax - con_size,),
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
            y_range=(rect_pcmpgr_in.ymin + con_size, rect_pcmpgr_in.ymax - con_size,),
            via_enclosure=(con_comp_enc, con_comp_enc),
            via_layer=layer["contact"],
            via_size=(con_size, con_size),
            via_spacing=(con_sp, con_sp),
        )
    )  # right contact

    c.add_ref(
        via_generator(
            x_range=(rect_pcmpgr_in.xmax, rect_pcmpgr_out.xmax),
            y_range=(rect_pcmpgr_in.ymin + con_size, rect_pcmpgr_in.ymax - con_size,),
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
            size=((comp_m1_in.size[0]) + 2 * grw, (comp_m1_in.size[1]) + 2 * grw,),
            layer=layer["metal1"],
        )
    )
    comp_m1_out.move((rect_pcmpgr_in.xmin - grw, rect_pcmpgr_in.ymin - grw))
    c.add_ref(
        gf.geometry.boolean(
            A=rect_pcmpgr_out, B=rect_pcmpgr_in, operation="A-B", layer=layer["metal1"],
        )
    )  # metal1 guardring

    return c


@gf.cell
def plus_res_inst(
    l_res: float = 0.1,
    w_res: float = 0.1,
    res_type: str = "nplus_s",
    sub: bool = 0,
    cmp_res_ext: float = 0.1,
    con_enc: float = 0.1,
    cmp_imp_layer: LayerSpec = layer["nplus"],
    sub_imp_layer: LayerSpec = layer["pplus"],
    lbl: bool = 0,
    r0_lbl: str = "",
    r1_lbl: str = "",
    sub_lbl: str = "",
) -> gf.Component:

    c = gf.Component()

    sub_w: float = 0.36
    np_enc_cmp: float = 0.16
    pp_enc_cmp: float = 0.16
    comp_spacing: float = 0.72
    sab_res_ext = 0.22
    cmp_area = 0.203
    sab_area = 2.01

    res_mk = c.add_ref(
        gf.components.rectangle(size=(l_res, w_res), layer=layer["res_mk"])
    )

    if "plus_u" in res_type:

        if (res_mk.size[0] * (res_mk.size[1] + (2 * sab_res_ext))) < sab_area:
            sab_rect_size = (res_mk.size[0], round(sab_area / res_mk.size[0], 3))
        else:
            sab_rect_size = (res_mk.size[0], (res_mk.size[1] + (2 * sab_res_ext)))

        sab_rect = c.add_ref(
            gf.components.rectangle(size=sab_rect_size, layer=layer["sab"],)
        )
        sab_rect.center = res_mk.center

        np_enc_cmp: float = 0.18
        pp_enc_cmp: float = 0.18

    cmp = c.add_ref(
        gf.components.rectangle(
            size=(res_mk.size[0] + (2 * cmp_res_ext), res_mk.size[1]),
            layer=layer["comp"],
        )
    )
    cmp.xmin = res_mk.xmin - cmp_res_ext
    cmp.ymin = res_mk.ymin

    cmp_con = via_stack(
        x_range=(cmp.xmin, res_mk.xmin + con_enc),
        y_range=(cmp.ymin, cmp.ymax),
        base_layer=layer["comp"],
        metal_level=1,
    )

    cmp_con_arr = c.add_array(
        component=cmp_con,
        rows=1,
        columns=2,
        spacing=(cmp_res_ext - con_enc + res_mk.size[0], 0),
    )  # comp contact array

    # labels generation
    if lbl == 1:
        c.add_label(
            r0_lbl,
            position=(
                cmp_con_arr.xmin + (cmp_con.size[0] / 2),
                cmp_con_arr.ymin + (cmp_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )
        c.add_label(
            r1_lbl,
            position=(
                cmp_con_arr.xmax - (cmp_con.size[0] / 2),
                cmp_con_arr.ymin + (cmp_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

    cmp_imp = c.add_ref(
        gf.components.rectangle(
            size=(cmp.size[0] + (2 * np_enc_cmp), cmp.size[1] + (2 * np_enc_cmp)),
            layer=cmp_imp_layer,
        )
    )
    cmp_imp.xmin = cmp.xmin - np_enc_cmp
    cmp_imp.ymin = cmp.ymin - np_enc_cmp

    if sub == 1:

        if (sub_w * w_res) < cmp_area:
            sub_rect_size = (sub_w, round(cmp_area / sub_w, 3))
        else:
            sub_rect_size = (sub_w, w_res)

        sub_rect = c.add_ref(
            gf.components.rectangle(size=sub_rect_size, layer=layer["comp"])
        )
        sub_rect.center = cmp.center
        sub_rect.xmax = cmp.xmin - comp_spacing

        # sub_rect contact
        sub_con = c.add_ref(
            via_stack(
                x_range=(sub_rect.xmin, sub_rect.xmax),
                y_range=(sub_rect.ymin, sub_rect.ymax),
                base_layer=layer["comp"],
                metal_level=1,
            )
        )

        sub_imp = c.add_ref(
            gf.components.rectangle(
                size=(
                    sub_rect.size[0] + (2 * pp_enc_cmp),
                    sub_rect.size[1] + (2 * pp_enc_cmp),
                ),
                layer=sub_imp_layer,
            )
        )
        sub_imp.xmin = sub_rect.xmin - pp_enc_cmp
        sub_imp.ymin = sub_rect.ymin - pp_enc_cmp

        # label generation
        if lbl == 1:
            c.add_label(
                sub_lbl,
                position=(
                    sub_con.xmin + (sub_con.size[0] / 2),
                    sub_con.ymin + (sub_con.size[1] / 2),
                ),
                layer=layer["metal1_label"],
            )

    return c


def draw_nplus_res(
    layout,
    l_res: float = 0.1,
    w_res: float = 0.1,
    res_type: str = "nplus_s",
    sub: bool = 0,
    deepnwell: bool = 0,
    pcmpgr: bool = 0,
    lbl: bool = 0,
    r0_lbl: str = "",
    r1_lbl: str = "",
    sub_lbl: str = "",
) -> gf.Component:

    c = gf.Component("res_dev")

    lvpwell_enc_cmp = 0.43
    dn_enc_lvpwell = 2.5
    sub_w = 0.36

    if res_type == "nplus_s":
        cmp_res_ext = 0.29
        con_enc = 0.07
    else:
        cmp_res_ext = 0.52
        con_enc = 0.0

    # adding res inst
    r_inst = c.add_ref(
        plus_res_inst(
            l_res=l_res,
            w_res=w_res,
            res_type=res_type,
            sub=sub,
            cmp_res_ext=cmp_res_ext,
            con_enc=con_enc,
            cmp_imp_layer=layer["nplus"],
            sub_imp_layer=layer["pplus"],
            lbl=lbl,
            r0_lbl=r0_lbl,
            r1_lbl=r1_lbl,
            sub_lbl=sub_lbl,
        )
    )

    if deepnwell == 1:
        lvpwell = c.add_ref(
            gf.components.rectangle(
                size=(
                    r_inst.size[0] + (2 * lvpwell_enc_cmp),
                    r_inst.size[1] + (2 * lvpwell_enc_cmp),
                ),
                layer=layer["lvpwell"],
            )
        )
        lvpwell.xmin = r_inst.xmin - lvpwell_enc_cmp
        lvpwell.ymin = r_inst.ymin - lvpwell_enc_cmp

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
            c.add_ref(pcmpgr_gen(dn_rect=dn_rect, grw=sub_w))

    c.write_gds("res_temp.gds")
    layout.read("res_temp.gds")
    cell_name = "res_dev"
    os.remove("res_temp.gds")

    return layout.cell(cell_name)


def draw_pplus_res(
    layout,
    l_res: float = 0.1,
    w_res: float = 0.1,
    res_type: str = "pplus_s",
    sub: bool = 0,
    deepnwell: bool = 0,
    pcmpgr: bool = 0,
    lbl: bool = 0,
    r0_lbl: str = "",
    r1_lbl: str = "",
    sub_lbl: str = "",
) -> gf.Component:

    c = gf.Component("res_dev")

    nw_enc_pcmp = 0.6
    dn_enc_ncmp = 0.66
    dn_enc_pcmp = 1.02
    sub_w = 0.36

    if res_type == "pplus_s":
        cmp_res_ext = 0.29
        con_enc = 0.07
    else:
        cmp_res_ext = 0.52
        con_enc = 0.0

    # adding res inst
    r_inst = c.add_ref(
        plus_res_inst(
            l_res=l_res,
            w_res=w_res,
            res_type=res_type,
            sub=1,
            cmp_res_ext=cmp_res_ext,
            con_enc=con_enc,
            cmp_imp_layer=layer["pplus"],
            sub_imp_layer=layer["nplus"],
            lbl=lbl,
            r0_lbl=r0_lbl,
            r1_lbl=r1_lbl,
            sub_lbl=sub_lbl,
        )
    )

    if deepnwell == 1:

        dn_rect = c.add_ref(
            gf.components.rectangle(
                size=(
                    r_inst.size[0] + (dn_enc_pcmp + dn_enc_ncmp),
                    r_inst.size[1] + (2 * dn_enc_pcmp),
                ),
                layer=layer["dnwell"],
            )
        )
        dn_rect.xmax = r_inst.xmax + dn_enc_pcmp
        dn_rect.ymin = r_inst.ymin - dn_enc_pcmp

        if pcmpgr == 1:
            c.add_ref(pcmpgr_gen(dn_rect=dn_rect, grw=sub_w))

    else:

        nw_rect = c.add_ref(
            gf.components.rectangle(
                size=(
                    r_inst.size[0] + (2 * nw_enc_pcmp),
                    r_inst.size[1] + (2 * nw_enc_pcmp),
                ),
                layer=layer["nwell"],
            )
        )
        nw_rect.xmin = r_inst.xmin - nw_enc_pcmp
        nw_rect.ymin = r_inst.ymin - nw_enc_pcmp

    c.write_gds("res_temp.gds")
    layout.read("res_temp.gds")
    cell_name = "res_dev"
    os.remove("res_temp.gds")

    return layout.cell(cell_name)


@gf.cell
def polyf_res_inst(
    l_res: float = 0.1,
    w_res: float = 0.1,
    res_type: str = "npolyf_s",
    pl_res_ext: float = 0.1,
    con_enc: float = 0.1,
    pl_imp_layer: LayerSpec = layer["nplus"],
    sub_imp_layer: LayerSpec = layer["pplus"],
    lbl: bool = 0,
    r0_lbl: str = "",
    r1_lbl: str = "",
    sub_lbl: str = "",
    sub_sp: float = 0.1,
) -> gf.Component:

    c = gf.Component()

    sub_w: float = 0.36
    np_enc_poly2 = 0.3
    pp_enc_cmp: float = 0.16
    comp_spacing: float = 0.46 + sub_sp
    sab_res_ext = 0.28
    cmp_area = 0.203
    sab_area = 2.01

    res_mk = c.add_ref(
        gf.components.rectangle(size=(l_res, w_res), layer=layer["res_mk"])
    )

    if "polyf_u" in res_type:

        if (res_mk.size[0] * (res_mk.size[1] + (2 * sab_res_ext))) < sab_area:
            sab_rect_size = (res_mk.size[0], round(sab_area / res_mk.size[0], 3))
        else:
            sab_rect_size = (res_mk.size[0], (res_mk.size[1] + (2 * sab_res_ext)))

        sab_rect = c.add_ref(
            gf.components.rectangle(size=sab_rect_size, layer=layer["sab"],)
        )
        sab_rect.center = res_mk.center

    pl = c.add_ref(
        gf.components.rectangle(
            size=(res_mk.size[0] + (2 * pl_res_ext), res_mk.size[1]),
            layer=layer["poly2"],
        )
    )
    pl.xmin = res_mk.xmin - pl_res_ext
    pl.ymin = res_mk.ymin

    pl_con = via_stack(
        x_range=(pl.xmin, res_mk.xmin + con_enc),
        y_range=(pl.ymin, pl.ymax),
        base_layer=layer["poly2"],
        metal_level=1,
    )

    pl_con_arr = c.add_array(
        component=pl_con,
        rows=1,
        columns=2,
        spacing=(pl_res_ext - con_enc + res_mk.size[0], 0),
    )  # comp contact array

    pl_imp = c.add_ref(
        gf.components.rectangle(
            size=(pl.size[0] + (2 * np_enc_poly2), pl.size[1] + (2 * np_enc_poly2)),
            layer=pl_imp_layer,
        )
    )
    pl_imp.xmin = pl.xmin - np_enc_poly2
    pl_imp.ymin = pl.ymin - np_enc_poly2

    if (sub_w * w_res) < cmp_area:
        sub_rect_size = (sub_w, round(cmp_area / sub_w, 3))
    else:
        sub_rect_size = (sub_w, w_res)

    sub_rect = c.add_ref(
        gf.components.rectangle(size=sub_rect_size, layer=layer["comp"])
    )
    sub_rect.center = pl.center
    sub_rect.xmax = pl.xmin - comp_spacing

    # sub_rect contact
    sub_con = c.add_ref(
        via_stack(
            x_range=(sub_rect.xmin, sub_rect.xmax),
            y_range=(sub_rect.ymin, sub_rect.ymax),
            base_layer=layer["comp"],
            metal_level=1,
        )
    )

    sub_imp = c.add_ref(
        gf.components.rectangle(
            size=(
                sub_rect.size[0] + (2 * pp_enc_cmp),
                sub_rect.size[1] + (2 * pp_enc_cmp),
            ),
            layer=sub_imp_layer,
        )
    )
    sub_imp.xmin = sub_rect.xmin - pp_enc_cmp
    sub_imp.ymin = sub_rect.ymin - pp_enc_cmp

    # labels generation
    if lbl == 1:
        c.add_label(
            r0_lbl,
            position=(
                pl_con_arr.xmin + (pl_con.size[0] / 2),
                pl_con_arr.ymin + (pl_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )
        c.add_label(
            r1_lbl,
            position=(
                pl_con_arr.xmax - (pl_con.size[0] / 2),
                pl_con_arr.ymin + (pl_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

        c.add_label(
            sub_lbl,
            position=(
                sub_con.xmin + (sub_con.size[0] / 2),
                sub_con.ymin + (sub_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

    return c


def draw_npolyf_res(
    layout,
    l_res: float = 0.1,
    w_res: float = 0.1,
    res_type: str = "npolyf_s",
    deepnwell: bool = 0,
    pcmpgr: bool = 0,
    lbl: bool = 0,
    r0_lbl: str = "",
    r1_lbl: str = "",
    sub_lbl: str = "",
) -> gf.Component:

    c = gf.Component("res_dev")

    sub_w = 0.36
    sub_sp = 0.26 if deepnwell == 0 else 0.4
    np_enc_cmp = 0.16
    dn_enc_cmp = 0.66 - np_enc_cmp

    if res_type == "npolyf_s":
        pl_res_ext = 0.29
        con_enc = 0.07
    else:
        pl_res_ext = 0.66
        con_enc = 0.0

    sub_imp = layer["nplus"] if deepnwell == 1 else layer["pplus"]

    # adding res inst
    r_inst = c.add_ref(
        polyf_res_inst(
            l_res=l_res,
            w_res=w_res,
            res_type=res_type,
            pl_res_ext=pl_res_ext,
            con_enc=con_enc,
            pl_imp_layer=layer["nplus"],
            sub_imp_layer=sub_imp,
            lbl=lbl,
            r0_lbl=r0_lbl,
            r1_lbl=r1_lbl,
            sub_lbl=sub_lbl,
            sub_sp=sub_sp,
        )
    )

    if deepnwell == 1:

        dn_rect = c.add_ref(
            gf.components.rectangle(
                size=(
                    r_inst.size[0] + (2 * dn_enc_cmp),
                    r_inst.size[1] + (2 * dn_enc_cmp),
                ),
                layer=layer["dnwell"],
            )
        )
        dn_rect.center = r_inst.center

        if pcmpgr == 1:
            c.add_ref(pcmpgr_gen(dn_rect=dn_rect, grw=sub_w))

    c.write_gds("res_temp.gds")
    layout.read("res_temp.gds")
    cell_name = "res_dev"
    os.remove("res_temp.gds")

    return layout.cell(cell_name)


def draw_ppolyf_res(
    layout,
    l_res: float = 0.1,
    w_res: float = 0.1,
    res_type: str = "ppolyf_s",
    deepnwell: bool = 0,
    pcmpgr: bool = 0,
    lbl: bool = 0,
    r0_lbl: str = "",
    r1_lbl: str = "",
    sub_lbl: str = "",
) -> gf.Component:

    c = gf.Component("res_dev")

    sub_w = 0.36
    dn_enc_ncmp = 0.66
    dn_enc_poly2 = 1.34

    if res_type == "ppolyf_s":
        pl_res_ext = 0.29
        con_enc = 0.07
    else:
        pl_res_ext = 0.66
        con_enc = 0.0

    if deepnwell == 1:
        sub_layer = layer["nplus"]
        sub_sp = 0.26
    else:
        sub_layer = layer["pplus"]
        sub_sp = 0.4

    # adding res inst
    r_inst = c.add_ref(
        polyf_res_inst(
            l_res=l_res,
            w_res=w_res,
            res_type=res_type,
            pl_res_ext=pl_res_ext,
            con_enc=con_enc,
            pl_imp_layer=layer["pplus"],
            sub_imp_layer=sub_layer,
            lbl=lbl,
            r0_lbl=r0_lbl,
            r1_lbl=r1_lbl,
            sub_lbl=sub_lbl,
            sub_sp=sub_sp,
        )
    )

    if deepnwell == 1:

        dn_rect = c.add_ref(
            gf.components.rectangle(
                size=(
                    r_inst.size[0] + (dn_enc_poly2 + dn_enc_ncmp),
                    r_inst.size[1] + (2 * dn_enc_poly2),
                ),
                layer=layer["dnwell"],
            )
        )
        dn_rect.xmax = r_inst.xmax + dn_enc_poly2
        dn_rect.ymin = r_inst.ymin - dn_enc_poly2

        if pcmpgr == 1:
            c.add_ref(pcmpgr_gen(dn_rect=dn_rect, grw=sub_w))

    c.write_gds("res_temp.gds")
    layout.read("res_temp.gds")
    cell_name = "res_dev"
    os.remove("res_temp.gds")

    return layout.cell(cell_name)


def draw_ppolyf_u_high_Rs_res(
    layout,
    l_res: float = 0.42,
    w_res: float = 0.42,
    volt: str = "3.3V",
    deepnwell: bool = 0,
    pcmpgr: bool = 0,
    lbl: bool = 0,
    r0_lbl: str = "",
    r1_lbl: str = "",
    sub_lbl: str = "",
) -> gf.Component:

    c = gf.Component("res_dev")

    dn_enc_ncmp = 0.62 if volt == "3.3V" else 0.66
    dn_enc_poly2 = 1.34

    pl_res_ext = 0.64

    sub_w: float = 0.42
    pp_enc_poly2 = 0.18
    pp_enc_cmp: float = 0.02
    comp_spacing: float = 0.7
    sab_res_ext = (0.1, 0.28)
    con_size = 0.36
    resis_enc = (1.04, 0.4)
    dg_enc_dn = 0.5
    np_pp_area = 0.351
    sab_area = 2.01

    res_mk = c.add_ref(
        gf.components.rectangle(size=(l_res, w_res), layer=layer["res_mk"])
    )

    resis_mk = c.add_ref(
        gf.components.rectangle(
            size=(
                res_mk.size[0] + (2 * resis_enc[0]),
                res_mk.size[1] + (2 * resis_enc[1]),
            ),
            layer=layer["resistor"],
        )
    )

    resis_mk.xmin = res_mk.xmin - resis_enc[0]
    resis_mk.ymin = res_mk.ymin - resis_enc[1]

    if (
        (res_mk.size[0] + (2 * sab_res_ext[0]))
        * (res_mk.size[1] + (2 * sab_res_ext[1]))
    ) < sab_area:
        sab_rect_size = (
            (res_mk.size[0] + (2 * sab_res_ext[0])),
            round(sab_area / (res_mk.size[0] + (2 * sab_res_ext[0])), 3),
        )
    else:
        sab_rect_size = (
            (res_mk.size[0] + (2 * sab_res_ext[0])),
            (res_mk.size[1] + (2 * sab_res_ext[1])),
        )

    sab_rect = c.add_ref(
        gf.components.rectangle(size=sab_rect_size, layer=layer["sab"],)
    )
    sab_rect.center = res_mk.center

    pl = c.add_ref(
        gf.components.rectangle(
            size=(res_mk.size[0] + (2 * pl_res_ext), res_mk.size[1]),
            layer=layer["poly2"],
        )
    )
    pl.xmin = res_mk.xmin - pl_res_ext
    pl.ymin = res_mk.ymin

    pl_con = via_stack(
        x_range=(pl.xmin, pl.xmin + con_size),
        y_range=(pl.ymin, pl.ymax),
        base_layer=layer["poly2"],
        metal_level=1,
    )

    pl_con_arr = c.add_array(
        component=pl_con, rows=1, columns=2, spacing=(pl.size[0] - con_size, 0),
    )  # comp contact array

    pplus = gf.components.rectangle(
        size=(pl_res_ext + pp_enc_poly2, pl.size[1] + (2 * pp_enc_poly2)),
        layer=layer["pplus"],
    )

    pplus_arr = c.add_array(
        component=pplus, rows=1, columns=2, spacing=(pplus.size[0] + res_mk.size[0], 0)
    )

    pplus_arr.xmin = pl.xmin - pp_enc_poly2
    pplus_arr.ymin = pl.ymin - pp_enc_poly2

    sub_rect = c.add_ref(
        gf.components.rectangle(size=(sub_w, w_res), layer=layer["comp"])
    )
    sub_rect.xmax = pl.xmin - comp_spacing
    sub_rect.ymin = pl.ymin

    # sub_rect contact
    sub_con = c.add_ref(
        via_stack(
            x_range=(sub_rect.xmin, sub_rect.xmax),
            y_range=(sub_rect.ymin, sub_rect.ymax),
            base_layer=layer["comp"],
            metal_level=1,
        )
    )

    # labels generation
    if lbl == 1:
        c.add_label(
            r0_lbl,
            position=(
                pl_con_arr.xmin + (pl_con.size[0] / 2),
                pl_con_arr.ymin + (pl_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )
        c.add_label(
            r1_lbl,
            position=(
                pl_con_arr.xmax - (pl_con.size[0] / 2),
                pl_con_arr.ymin + (pl_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

        c.add_label(
            sub_lbl,
            position=(
                sub_con.xmin + (sub_con.size[0] / 2),
                sub_con.ymin + (sub_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

    if deepnwell == 1:
        sub_layer = layer["nplus"]
    else:
        sub_layer = layer["pplus"]

    if (
        (sub_rect.size[0] + (2 * pp_enc_cmp)) * (pl.size[1] + (2 * pp_enc_cmp))
    ) < np_pp_area:
        sub_imp_size = (
            sub_rect.size[0] + (2 * pp_enc_cmp),
            round(np_pp_area / (pl.size[1] + (2 * pp_enc_cmp)), 3),
        )
    else:
        sub_imp_size = (
            sub_rect.size[0] + (2 * pp_enc_cmp),
            pl.size[1] + (2 * pp_enc_cmp),
        )

    sub_imp = c.add_ref(gf.components.rectangle(size=sub_imp_size, layer=sub_layer,))
    sub_imp.center = sub_rect.center

    if deepnwell == 1:

        dn_rect = c.add_ref(
            gf.components.rectangle(
                size=(
                    (pl.xmax - sub_rect.xmin) + (dn_enc_poly2 + dn_enc_ncmp),
                    pl.size[1] + (2 * dn_enc_poly2),
                ),
                layer=layer["dnwell"],
            )
        )
        dn_rect.xmax = pl.xmax + dn_enc_poly2
        dn_rect.ymin = pl.ymin - dn_enc_poly2

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

        if pcmpgr == 1:
            c.add_ref(pcmpgr_gen(dn_rect=dn_rect, grw=sub_w))

    else:
        if volt == "5/6V":
            dg = c.add_ref(
                gf.components.rectangle(
                    size=(resis_mk.size[0], resis_mk.size[1]), layer=layer["dualgate"]
                )
            )

            dg.xmin = resis_mk.xmin
            dg.ymin = resis_mk.ymin

    c.write_gds("res_temp.gds")
    layout.read("res_temp.gds")
    cell_name = "res_dev"
    os.remove("res_temp.gds")

    return layout.cell(cell_name)


def draw_well_res(
    layout,
    l_res: float = 0.42,
    w_res: float = 0.42,
    res_type: str = "nwell",
    pcmpgr: bool = 0,
    lbl: bool = 0,
    r0_lbl: str = "",
    r1_lbl: str = "",
    sub_lbl: str = "",
) -> gf.Component:

    c = gf.Component("res_dev")

    nw_res_ext = 0.48
    nw_res_enc = 0.5
    nw_enc_cmp = 0.12

    sub_w: float = 0.36
    pp_enc_cmp: float = 0.16
    nw_comp_spacing: float = 0.72
    dn_enc_lvpwell = 2.5

    if res_type == "pwell":
        cmp_imp_layer = layer["pplus"]
        sub_imp_layer = layer["nplus"]
        well_layer = layer["lvpwell"]
    else:
        cmp_imp_layer = layer["nplus"]
        sub_imp_layer = layer["pplus"]
        well_layer = layer["nwell"]

    res_mk = c.add_ref(
        gf.components.rectangle(
            size=(l_res, w_res + (2 * nw_res_enc)), layer=layer["res_mk"]
        )
    )

    well_rect = c.add_ref(
        gf.components.rectangle(
            size=(res_mk.size[0] + (2 * nw_res_ext), w_res), layer=well_layer
        )
    )
    well_rect.xmin = res_mk.xmin - nw_res_ext
    well_rect.ymin = res_mk.ymin + nw_res_enc

    @gf.cell
    def comp_related_gen(size: Float2 = (0.42, 0.42)) -> gf.Component:

        c = gf.Component()

        cmp = c.add_ref(gf.components.rectangle(size=size, layer=layer["comp"]))
        cmp.xmin = well_rect.xmin + nw_enc_cmp
        cmp.ymin = well_rect.ymin + nw_enc_cmp

        c.add_ref(
            via_stack(
                x_range=(cmp.xmin, cmp.xmax),
                y_range=(cmp.ymin, cmp.ymax),
                base_layer=layer["comp"],
                metal_level=1,
            )
        )  # contact

        return c

    con_polys = comp_related_gen(
        size=(
            res_mk.xmin - well_rect.xmin - nw_enc_cmp,
            well_rect.size[1] - (2 * nw_enc_cmp),
        )
    )

    con_polys_arr = c.add_array(
        component=con_polys,
        rows=1,
        columns=2,
        spacing=(well_rect.size[0] - (2 * nw_enc_cmp) - con_polys.size[0], 0),
    )  # comp and its related contact array

    nplus_rect = gf.components.rectangle(
        size=(
            con_polys.size[0] + (2 * pp_enc_cmp),
            con_polys.size[1] + (2 * pp_enc_cmp),
        ),
        layer=cmp_imp_layer,
    )
    nplus_arr = c.add_array(
        component=nplus_rect,
        rows=1,
        columns=2,
        spacing=(well_rect.size[0] - (2 * nw_enc_cmp) - con_polys.size[0], 0),
    )
    nplus_arr.xmin = con_polys.xmin - pp_enc_cmp
    nplus_arr.ymin = con_polys.ymin - pp_enc_cmp

    sub_rect = c.add_ref(
        gf.components.rectangle(size=(sub_w, well_rect.size[1]), layer=layer["comp"])
    )
    sub_rect.xmax = well_rect.xmin - nw_comp_spacing
    sub_rect.ymin = well_rect.ymin

    # sub_rect contact
    sub_con = c.add_ref(
        via_stack(
            x_range=(sub_rect.xmin, sub_rect.xmax),
            y_range=(sub_rect.ymin, sub_rect.ymax),
            base_layer=layer["comp"],
            metal_level=1,
        )
    )

    sub_imp = c.add_ref(
        gf.components.rectangle(
            size=(
                sub_rect.size[0] + (2 * pp_enc_cmp),
                well_rect.size[1] + (2 * pp_enc_cmp),
            ),
            layer=sub_imp_layer,
        )
    )
    sub_imp.xmin = sub_rect.xmin - pp_enc_cmp
    sub_imp.ymin = sub_rect.ymin - pp_enc_cmp

    if res_type == "pwell":

        dn_rect = c.add_ref(
            gf.components.rectangle(
                size=(
                    well_rect.size[0] + (2 * dn_enc_lvpwell),
                    well_rect.size[1] + (2 * dn_enc_lvpwell),
                ),
                layer=layer["dnwell"],
            )
        )
        dn_rect.xmin = well_rect.xmin - dn_enc_lvpwell
        dn_rect.ymin = well_rect.ymin - dn_enc_lvpwell

        if pcmpgr == 1:
            c.add_ref(pcmpgr_gen(dn_rect=dn_rect, grw=sub_w))

    # labels generation
    if lbl == 1:
        c.add_label(
            r0_lbl,
            position=(
                con_polys_arr.xmin + (con_polys.size[0] / 2),
                con_polys_arr.ymin + (con_polys.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )
        c.add_label(
            r1_lbl,
            position=(
                con_polys_arr.xmax - (con_polys.size[0] / 2),
                con_polys_arr.ymin + (con_polys.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

        c.add_label(
            sub_lbl,
            position=(
                sub_con.xmin + (sub_con.size[0] / 2),
                sub_con.ymin + (sub_con.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

    c.write_gds("res_temp.gds")
    layout.read("res_temp.gds")
    cell_name = "res_dev"
    os.remove("res_temp.gds")

    return layout.cell(cell_name)
