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
## MOS capacitor Pcells Generators for Klayout of GF180MCU
########################################################################################################################

import gdsfactory as gf
from gdsfactory.typings import Float2, LayerSpec

from .via_generator import via_generator, via_stack
from .layers_def import layer

import numpy as np
import os


@gf.cell
def cap_mos_inst(
    lc: float = 0.1,
    wc: float = 0.1,
    cmp_w: float = 0.1,
    con_w: float = 0.1,
    pl_l: float = 0.1,
    cmp_ext: float = 0.1,
    pl_ext: float = 0.1,
    implant_layer: LayerSpec = layer["nplus"],
    implant_enc: Float2 = (0.1, 0.1),
    lbl: bool = 0,
    g_lbl: str = "",
    lvpwell: bool = 1,
    nwell: bool = 1,
    nw_enc_cmp: float = 0.16,
) -> gf.Component:
    """Returns mos cap simple instance

    Args :
        lc : length of mos_cap
        ws : width of mos_cap
        cmp_w : width of layer["comp"]
        con_w : min width of comp contain contact
        pl_l : length od layer["poly2"]
        cmp_ext : comp extension beyond poly2
        pl_ext : poly2 extension beyond comp
        implant_layer : Layer of implant [nplus,pplus]
        implant_enc : enclosure of implant_layer to comp
    """

    c_inst = gf.Component()

    m1_sp = 0.28

    cmp = c_inst.add_ref(gf.components.rectangle(size=(cmp_w, wc), layer=layer["comp"]))

    cap_mk = c_inst.add_ref(
        gf.components.rectangle(
            size=(cmp.size[0], cmp.size[1]), layer=layer["mos_cap_mk"]
        )
    )
    cap_mk.xmin = cmp.xmin
    cap_mk.ymin = cmp.ymin

    if lvpwell == 0:
        lvpwell_rect = c_inst.add_ref(
            gf.components.rectangle(
                size=(cap_mk.size[0], cap_mk.size[1]), layer=layer["lvpwell"]
            )
        )
        lvpwell_rect.center = cap_mk.center

    if nwell == 0:
        nwell_rect = c_inst.add_ref(
            gf.components.rectangle(
                size=(cmp.size[0] + (2 * nw_enc_cmp), cmp.size[1] + (2 * nw_enc_cmp)),
                layer=layer["nwell"],
            )
        )
        nwell_rect.center = cmp.center

    cmp_con_el = via_stack(
        x_range=(cmp.xmin, cmp.xmin + con_w),
        y_range=(cmp.ymin, cmp.ymax),
        base_layer=layer["comp"],
        metal_level=1,
    )

    c_inst.add_array(
        component=cmp_con_el, rows=1, columns=2, spacing=(cmp_w - con_w, 0),
    )  # comp contact

    imp_rect = c_inst.add_ref(
        gf.components.rectangle(
            size=(
                cmp.size[0] + (2 * implant_enc[0]),
                cmp.size[1] + (2 * implant_enc[1]),
            ),
            layer=implant_layer,
        )
    )
    imp_rect.xmin = cmp.xmin - implant_enc[0]
    imp_rect.ymin = cmp.ymin - implant_enc[1]

    poly = c_inst.add_ref(
        gf.components.rectangle(size=(lc, pl_l), layer=layer["poly2"])
    )

    poly.xmin = cmp.xmin + cmp_ext
    poly.ymin = cmp.ymin - pl_ext

    pl_con_el = via_stack(
        x_range=(poly.xmin + m1_sp, poly.xmax - m1_sp),
        y_range=(poly.ymin, poly.ymin + con_w),
        base_layer=layer["poly2"],
        metal_level=1,
    )

    pl_con = c_inst.add_array(
        component=pl_con_el, rows=2, columns=1, spacing=(0, pl_l - con_w),
    )

    # Gate labels_generation

    if lbl == 1:
        c_inst.add_label(
            g_lbl,
            position=(
                pl_con.xmin + (pl_con.size[0] / 2),
                pl_con.ymin + (pl_con_el.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

    pl_m1 = c_inst.add_ref(
        gf.components.rectangle(
            size=(pl_con.size[0], pl_con.size[1]), layer=layer["metal1"]
        )
    )
    pl_m1.xmin = pl_con.xmin
    pl_m1.ymin = pl_con.ymin

    return c_inst


def draw_cap_mos(
    layout,
    type: str = "cap_nmos",
    lc: float = 0.1,
    wc: float = 0.1,
    volt: str = "3.3V",
    deepnwell: bool = 0,
    pcmpgr: bool = 0,
    lbl: bool = 0,
    g_lbl: str = "",
    sd_lbl: str = "",
) -> gf.Component:
    """
    Usage:-
     used to draw NMOS capacitor (Outside DNWELL) by specifying parameters
    Arguments:-
     layout : Object of layout
     l      : Float of diff length
     w      : Float of diff width
    """

    c = gf.Component("cap_mos_dev")

    con_size = 0.22
    con_sp = 0.28
    con_comp_enc = 0.07
    con_pl_enc = 0.07
    cmp_ext = 0.15 - con_comp_enc
    pl_ext = 0.17 - con_pl_enc

    np_enc_gate: float = 0.23
    np_enc_cmp: float = 0.16

    dg_enc_cmp = 0.24
    dg_enc_poly = 0.4
    lvpwell_enc_ncmp = 0.43 if volt == "3.3V" else 0.6
    dn_enc_lvpwell = 2.5

    grw = 0.36

    m1_w = 1
    pcmpgr_enc_dn = 2.501
    m1_ext = 0.82
    comp_pp_enc: float = 0.16
    dnwell_enc_pcmp = 1.1

    dg_enc_dn = 0.5

    # end_cap: float = 0.22

    cmp_ed_w = con_size + (2 * con_comp_enc)
    cmp_w = (2 * (cmp_ed_w + cmp_ext)) + lc
    end_cap = pl_ext + cmp_ed_w

    pl_l = wc + (2 * end_cap)

    if "cap_nmos" in type:
        implant_layer = layer["nplus"]
        lvp_dis = 1 if "_b" in type else deepnwell
        nw_dis = 1
    else:
        implant_layer = layer["pplus"]
        lvp_dis = 1
        nw_dis = 1 if ("_b" in type or (deepnwell == 0 and pcmpgr == 1)) else deepnwell

    c_inst = c.add_ref(
        cap_mos_inst(
            cmp_w=cmp_w,
            lc=lc,
            wc=wc,
            pl_l=pl_l,
            cmp_ext=cmp_ed_w + cmp_ext,
            con_w=cmp_ed_w,
            pl_ext=end_cap,
            implant_layer=implant_layer,
            implant_enc=(np_enc_cmp, np_enc_gate),
            lbl=lbl,
            g_lbl=g_lbl,
            lvpwell=lvp_dis,
            nwell=nw_dis,
            nw_enc_cmp=lvpwell_enc_ncmp,
        )
    )

    cmp_m1_polys = c_inst.get_polygons(by_spec=layer["metal1"])
    cmp_m1_xmin = np.min(cmp_m1_polys[0][:, 0])
    cmp_m1_xmax = np.max(cmp_m1_polys[0][:, 0])
    cmp_m1_ymax = np.max(cmp_m1_polys[0][:, 1])

    # cmp_m1 = c.add_ref(gf.components.rectangle(size=(m1_w,w+m1_ext),layer=layer["metal1"]))
    cmp_m1_v = c.add_array(
        component=gf.components.rectangle(
            size=(m1_w, wc + m1_ext), layer=layer["metal1"]
        ),
        rows=1,
        columns=2,
        spacing=(m1_w + cmp_w - 2 * cmp_ed_w, 0),
    )
    cmp_m1_v.xmin = cmp_m1_xmin - (m1_w - (cmp_m1_xmax - cmp_m1_xmin))
    cmp_m1_v.ymax = cmp_m1_ymax

    cmp_m1_h = c.add_ref(
        gf.components.rectangle(size=(cmp_m1_v.size[0], m1_w), layer=layer["metal1"])
    )
    cmp_m1_h.xmin = cmp_m1_v.xmin
    cmp_m1_h.ymax = cmp_m1_v.ymin

    # sd labels generation
    if lbl == 1:
        c.add_label(
            sd_lbl,
            position=(
                cmp_m1_h.xmin + (cmp_m1_h.size[0] / 2),
                cmp_m1_h.ymin + (cmp_m1_h.size[1] / 2),
            ),
            layer=layer["metal1_label"],
        )

    # dualgate

    cmp_polys = c_inst.get_polygons(by_spec=layer["comp"])
    cmp_xmin = np.min(cmp_polys[0][:, 0])
    cmp_ymin = np.min(cmp_polys[0][:, 1])
    cmp_xmax = np.max(cmp_polys[0][:, 0])
    cmp_ymax = np.max(cmp_polys[0][:, 1])

    if "cap_nmos_b" in type:
        nwell = c.add_ref(
            gf.components.rectangle(
                size=(
                    cmp_xmax - cmp_xmin + (2 * np_enc_cmp),
                    cmp_ymax - cmp_ymin + (2 * np_enc_gate),
                ),
                layer=layer["nwell"],
            )
        )
        nwell.xmin = cmp_xmin - np_enc_cmp
        nwell.ymin = cmp_ymin - np_enc_gate

    if deepnwell == 1:

        if type == "cap_nmos":
            lvp_rect = c.add_ref(
                gf.components.rectangle(
                    size=(
                        c_inst.size[0] + (2 * lvpwell_enc_ncmp),
                        c_inst.size[1] + (2 * lvpwell_enc_ncmp),
                    ),
                    layer=layer["lvpwell"],
                )
            )

            lvp_rect.xmin = c_inst.xmin - lvpwell_enc_ncmp
            lvp_rect.ymin = c_inst.ymin - lvpwell_enc_ncmp

            dn_rect = c.add_ref(
                gf.components.rectangle(
                    size=(
                        lvp_rect.size[0] + (2 * dn_enc_lvpwell),
                        lvp_rect.size[1] + (2 * dn_enc_lvpwell),
                    ),
                    layer=layer["dnwell"],
                )
            )

            dn_rect.xmin = lvp_rect.xmin - dn_enc_lvpwell
            dn_rect.ymin = lvp_rect.ymin - dn_enc_lvpwell

        else:
            dn_rect = c.add_ref(
                gf.components.rectangle(
                    size=(
                        c_inst.size[0] + (2 * dnwell_enc_pcmp),
                        c_inst.size[1] + (2 * dnwell_enc_pcmp),
                    ),
                    layer=layer["dnwell"],
                )
            )

            dn_rect.xmin = c_inst.xmin - dnwell_enc_pcmp
            dn_rect.ymin = c_inst.ymin - dnwell_enc_pcmp

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

        pcmpgr_enc = dn_rect
        gr_imp = layer["pplus"]

    else:

        if volt == "5/6V":
            dg = c.add_ref(
                gf.components.rectangle(
                    size=(
                        c_inst.size[0] + (2 * dg_enc_cmp),
                        c_inst.size[1] + (2 * dg_enc_poly),
                    ),
                    layer=layer["dualgate"],
                )
            )
            dg.xmin = c_inst.xmin - dg_enc_cmp
            dg.ymin = c_inst.ymin - dg_enc_poly

        pcmpgr_enc = c_inst

        gr_imp = layer["nplus"] if ("pmos" in type) else layer["pplus"]

    if pcmpgr == 1:

        c_temp_gr = gf.Component("temp_store guard ring")
        rect_pcmpgr_in = c_temp_gr.add_ref(
            gf.components.rectangle(
                size=(
                    (pcmpgr_enc.xmax - pcmpgr_enc.xmin) + 2 * pcmpgr_enc_dn,
                    (pcmpgr_enc.ymax - pcmpgr_enc.ymin) + 2 * pcmpgr_enc_dn,
                ),
                layer=layer["comp"],
            )
        )
        rect_pcmpgr_in.move(
            (pcmpgr_enc.xmin - pcmpgr_enc_dn, pcmpgr_enc.ymin - pcmpgr_enc_dn)
        )
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
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["comp"],
            )
        )  # guardring Bullk

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
            gf.geometry.boolean(A=psdm_out, B=psdm_in, operation="A-B", layer=gr_imp)
        )  # psdm

        # generating contacts

        if deepnwell == 0 and gr_imp == layer["nplus"]:
            print("here")

            nwell_rect = c.add_ref(
                gf.components.rectangle(
                    size=(psdm_out.size[0], psdm_out.size[1]), layer=layer["nwell"]
                )
            )
            nwell_rect.center = psdm_out.center

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
                size=((comp_m1_in.size[0]) + 2 * grw, (comp_m1_in.size[1]) + 2 * grw,),
                layer=layer["metal1"],
            )
        )
        comp_m1_out.move((rect_pcmpgr_in.xmin - grw, rect_pcmpgr_in.ymin - grw))
        c.add_ref(
            gf.geometry.boolean(
                A=rect_pcmpgr_out,
                B=rect_pcmpgr_in,
                operation="A-B",
                layer=layer["metal1"],
            )
        )  # guardring metal1

    c.write_gds("cap_mos_temp.gds")
    layout.read("cap_mos_temp.gds")
    cell_name = "cap_mos_dev"
    os.remove("cap_mos_temp.gds")

    return layout.cell(cell_name)
