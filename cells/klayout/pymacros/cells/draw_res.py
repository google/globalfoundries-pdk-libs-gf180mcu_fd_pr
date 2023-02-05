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
from .layers_def import *
from .via_generator import via_generator, via_stack


def draw_metal_res(
    layout, l_res: float = 0.1, w_res: float = 0.1, res_type: str = "rm1"
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
        m_layer = m1_layer
        res_layer = metal1_res_layer
    elif res_type == "rm2":
        m_layer = m2_layer
        res_layer = metal2_res_layer
    elif res_type == "rm3":
        m_layer = m3_layer
        res_layer = metal3_res_layer
    else:
        m_layer = metaltop_layer
        res_layer = metal6_res_layer

    res_mk = c.add_ref(gf.components.rectangle(size=(l_res, w_res), layer=res_layer))

    m_rect = c.add_ref(
        gf.components.rectangle(size=(l_res + (2 * m_ext), w_res), layer=m_layer)
    )
    m_rect.xmin = res_mk.xmin - m_ext
    m_rect.ymin = res_mk.ymin

    # creating layout and cell in klayout
    c.write_gds("res_temp.gds")
    layout.read("res_temp.gds")
    cell_name = "res_dev"

    return layout.cell(cell_name)


def draw_nplus_s_res(
    layout,
    l_res: float = 0.1,
    w_res: float = 0.1,
    sub: bool = 0,
    deepnwell: bool = 0,
    pcmpgr: bool = 0,
) -> gf.Component:

    c = gf.Component("res_dev")

    cmp_res_ext: float = 0.29
    sub_w: float = 0.36
    con_enc = 0.07
    np_enc_cmp: float = 0.16

    @gf.cell
    def res_inst(l_res: float = 0.1, w_res: float = 0.1, sub: bool = 0) -> gf.Component:

        c = gf.Component()

        res_mk = c.add_ref(
            gf.components.rectangle(size=(l_res, w_res), layer=res_mk_layer)
        )

        cmp = c.add_ref(
            gf.components.rectangle(
                size=(res_mk.size[0] + (2 * cmp_res_ext), res_mk.size[1]),
                layer=comp_layer,
            )
        )
        cmp.xmin = res_mk.xmin - cmp_res_ext
        cmp.ymin = res_mk.ymin

        cmp_con = via_stack(
            x_range=(cmp.xmin, res_mk.xmin + con_enc),
            y_range=(cmp.ymin, cmp.ymax),
            base_layer=comp_layer,
            metal_level=1,
        )

        c.add_array(
            component=cmp_con,
            rows=1,
            columns=2,
            spacing=(cmp_res_ext - con_enc + res_mk.size[0], 0),
        )  # comp contact array

        nplus = c.add_ref(
            gf.components.rectangle(
                size=(cmp.size[0] + (2 * np_enc_cmp), cmp.size[1] + (2 * np_enc_cmp)),
                layer=nplus_layer,
            )
        )
        nplus.xmin = cmp.xmin - np_enc_cmp
        nplus.ymin = cmp.ymin - np_enc_cmp

        return c

    # adding res inst
    r_inst = c.add_ref(res_inst(l_res=l_res, w_res=w_res, sub=sub))

    c.write_gds("res_temp.gds")
    layout.read("res_temp.gds")
    cell_name = "res_dev"

    return layout.cell(cell_name)
