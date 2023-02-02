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
from .via_generator import *


def draw_metal_res(layout, l, w, res_type) -> gf.Component:
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

    res_mk = c.add_ref(gf.components.rectangle(size=(l, w), layer=res_layer))

    m_rect = c.add_ref(
        gf.components.rectangle(size=(l + (2 * m_ext), w), layer=m_layer)
    )
    m_rect.xmin = res_mk.xmin - m_ext
    m_rect.ymin = res_mk.ymin

    # creating layout and cell in klayout
    c.write_gds(f"res_temp.gds")
    layout.read(f"res_temp.gds")
    cell_name = "res_dev"

    return layout.cell(cell_name)
