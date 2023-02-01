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

from .via_generator import *
from .layers_def import *

import numpy as np


@gf.cell
def cap_mos_inst(
    l: float = 0.1,
    w: float = 0.1,
    cmp_w: float = 0.1,
    con_w: float = 0.1,
    pl_l: float = 0.1,
    cmp_ext: float = 0.1,
    pl_ext: float = 0.1,
    implant_layer: LayerSpec = nplus_layer,
    implant_enc: Float2 = (0.1, 0.1),
) -> gf.Component:

    c_inst = gf.Component()

    cmp = c_inst.add_ref(gf.components.rectangle(size=(cmp_w, w), layer=comp_layer))

    cap_mk = c_inst.add_ref(
        gf.components.rectangle(size=(cmp.size[0], cmp.size[1]), layer=mos_cap_mk_layer)
    )
    cap_mk.xmin = cmp.xmin
    cap_mk.ymin = cmp.ymin

    cmp_con = c_inst.add_array(
        component=via_stack(
            x_range=(cmp.xmin, cmp.xmin + con_w),
            y_range=(cmp.ymin, cmp.ymax),
            base_layer=comp_layer,
            metal_level=1,
        ),
        rows=1,
        columns=2,
        spacing=(cmp_w - con_w, 0),
    )

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

    poly = c_inst.add_ref(gf.components.rectangle(size=(l, pl_l), layer=poly2_layer))

    poly.xmin = cmp.xmin + cmp_ext
    poly.ymin = cmp.ymin - pl_ext

    pl_con = c_inst.add_array(
        component=via_stack(
            x_range=(poly.xmin, poly.xmax),
            y_range=(poly.ymin, poly.ymin + con_w),
            base_layer=poly2_layer,
            metal_level=1,
        ),
        rows=2,
        columns=1,
        spacing=(0, pl_l - con_w),
    )

    pl_m1 = c_inst.add_ref(
        gf.components.rectangle(size=(pl_con.size[0], pl_con.size[1]), layer=m1_layer)
    )
    pl_m1.xmin = pl_con.xmin
    pl_m1.ymin = pl_con.ymin

    return c_inst


def draw_cap_mos(
    layout,
    type: str = "cap_nmos",
    l: float = 0.1,
    w: float = 0.1,
    volt: str = "3.3V",
    deepnwell: bool = 0,
    pcmpgr: bool = 0,
) -> gf.Component:
    """
    Usage:-
     used to draw NMOS capacitor (Outside DNWELL) by specifying parameters
    Arguments:-
     layout : Object of layout
     l      : Float of diff length
     w      : Float of diff width
    """

    c = gf.Component("cap_nmos_dev")

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
    lvpwell_enc_ncmp = 0.43
    dn_enc_lvpwell = 2.5

    grw = 0.36

    m1_w = 1
    pcmpgr_enc_dn = 2.5
    m1_ext = 0.82
    comp_pp_enc: float = 0.16
    dnwell_enc_pcmp = 1.1

    # end_cap: float = 0.22

    cmp_ed_w = con_size + (2 * con_comp_enc)
    cmp_w = (2 * (cmp_ed_w + cmp_ext)) + l
    end_cap = pl_ext + cmp_ed_w

    pl_l = w + (2 * end_cap)

    if type == "cap_nmos":
        implant_layer = nplus_layer
    else:
        implant_layer = pplus_layer

    c_inst = c.add_ref(
        cap_mos_inst(
            cmp_w=cmp_w,
            l=l,
            w=w,
            pl_l=pl_l,
            cmp_ext=cmp_ed_w + cmp_ext,
            con_w=cmp_ed_w,
            pl_ext=end_cap,
            implant_layer=implant_layer,
            implant_enc=(np_enc_cmp, np_enc_gate),
        )
    )

    cmp_m1_polys = c_inst.get_polygons(by_spec=m1_layer)
    cmp_m1_xmin = np.min(cmp_m1_polys[0][:, 0])
    cmp_m1_ymin = np.min(cmp_m1_polys[0][:, 1])
    cmp_m1_xmax = np.max(cmp_m1_polys[0][:, 0])
    cmp_m1_ymax = np.max(cmp_m1_polys[0][:, 1])

    # cmp_m1 = c.add_ref(gf.components.rectangle(size=(m1_w,w+m1_ext),layer=m1_layer))
    cmp_m1_v = c.add_array(
        component=gf.components.rectangle(size=(m1_w, w + m1_ext), layer=m1_layer),
        rows=1,
        columns=2,
        spacing=(m1_w + cmp_w - 2 * cmp_ed_w, 0),
    )
    cmp_m1_v.xmin = cmp_m1_xmin - (m1_w - (cmp_m1_xmax - cmp_m1_xmin))
    cmp_m1_v.ymax = cmp_m1_ymax

    cmp_m1_h = c.add_ref(
        gf.components.rectangle(size=(cmp_m1_v.size[0], m1_w), layer=m1_layer)
    )
    cmp_m1_h.xmin = cmp_m1_v.xmin
    cmp_m1_h.ymax = cmp_m1_v.ymin

    # dualgate

    if volt == "5/6V":
        dg = c.add_ref(
            gf.components.rectangle(
                size=(
                    c_inst.size[0] + (2 * dg_enc_cmp),
                    c_inst.size[1] + (2 * dg_enc_poly),
                ),
                layer=dualgate_layer,
            )
        )
        dg.xmin = c_inst.xmin - dg_enc_cmp
        dg.ymin = c_inst.ymin - dg_enc_poly

    if deepnwell == 1:

        if type == "cap_nmos":
            lvp_rect = c.add_ref(
                gf.components.rectangle(
                    size=(
                        c_inst.size[0] + (2 * lvpwell_enc_ncmp),
                        c_inst.size[1] + (2 * lvpwell_enc_ncmp),
                    ),
                    layer=lvpwell_layer,
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
                    layer=dnwell_layer,
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
                    layer=dnwell_layer,
                )
            )

            dn_rect.xmin = c_inst.xmin - dnwell_enc_pcmp
            dn_rect.ymin = c_inst.ymin - dnwell_enc_pcmp

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
                        (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * grw,
                        (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * grw,
                    ),
                    layer=comp_layer,
                )
            )
            rect_pcmpgr_out.move((rect_pcmpgr_in.xmin - grw, rect_pcmpgr_in.ymin - grw))
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
                        (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) - 2 * comp_pp_enc,
                        (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) - 2 * comp_pp_enc,
                    ),
                    layer=pplus_layer,
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
                    layer=pplus_layer,
                )
            )
            psdm_out.move(
                (
                    rect_pcmpgr_out.xmin - comp_pp_enc,
                    rect_pcmpgr_out.ymin - comp_pp_enc,
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
                    size=(
                        rect_pcmpgr_in.size[0],
                        rect_pcmpgr_in.size[1]
                        # (l_d) + 2 * comp_spacing,
                        # (c_inst.ymax - c_inst.ymin) + 2 * poly2_comp_spacing,
                    ),
                    layer=m1_layer,
                )
            )
            # comp_m1_in.move((-comp_spacing, c_inst.ymin - poly2_comp_spacing))

            comp_m1_out = c_temp_gr.add_ref(
                gf.components.rectangle(
                    size=(
                        (rect_pcmpgr_in.xmax - rect_pcmpgr_in.xmin) + 2 * grw,
                        (rect_pcmpgr_in.ymax - rect_pcmpgr_in.ymin) + 2 * grw,
                    ),
                    layer=m1_layer,
                )
            )
            comp_m1_out.move((rect_pcmpgr_in.xmin - grw, rect_pcmpgr_in.ymin - grw))
            m1 = c.add_ref(
                gf.geometry.boolean(
                    A=rect_pcmpgr_out,
                    B=rect_pcmpgr_in,
                    operation="A-B",
                    layer=m1_layer,
                )
            )

    c.write_gds("cap_nmos_temp.gds")
    layout.read("cap_nmos_temp.gds")
    cell_name = "cap_nmos_dev"

    return layout.cell(cell_name)
