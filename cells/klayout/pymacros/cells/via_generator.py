# Copyright 2022 Skywater 130nm pdk development
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

########################################################################################################################
# via Generator for skywater130
########################################################################################################################


from math import ceil, floor
import gdsfactory as gf
from gdsfactory.types import Float2, LayerSpec
from .layers_def import *


@gf.cell
def via_generator(
    x_range: Float2 = (0, 1),
    y_range: Float2 = (0, 1),
    via_size: Float2 = (0.17, 0.17),
    via_layer: LayerSpec = (66, 44),
    via_enclosure: Float2 = (0.06, 0.06),
    via_spacing: Float2 = (0.17, 0.17),
) -> gf.Component():

    """
    return only vias withen the range xrange and yrange while enclosing by via_enclosure
    and set number of rows and number of coloumns according to ranges and via size and spacing

    """

    c = gf.Component()

    width = x_range[1] - x_range[0]
    length = y_range[1] - y_range[0]
    nr = floor(length / (via_size[1] + via_spacing[1]))
    if (length - nr * via_size[1] - (nr - 1) * via_spacing[1]) / 2 < via_enclosure[1]:
        nr -= 1

    if nr < 1:
        nr = 1

    nc = ceil(width / (via_size[0] + via_spacing[0]))

    if (
        round(width - nc * via_size[0] - (nc - 1) * via_spacing[0], 2)
    ) / 2 < via_enclosure[0]:
        nc -= 1

    if nc < 1:
        nc = 1

    via_sp = (via_size[0] + via_spacing[0], via_size[1] + via_spacing[1])

    rect_via = gf.components.rectangle(size=via_size, layer=via_layer)

    via_arr = c.add_array(rect_via, rows=nr, columns=nc, spacing=via_sp)

    via_arr.move((x_range[0], y_range[0]))

    via_arr.movex((width - nc * via_size[0] - (nc - 1) * via_spacing[0]) / 2)
    via_arr.movey((length - nr * via_size[1] - (nr - 1) * via_spacing[1]) / 2)

    return c


@gf.cell
def via_stack(
    x_range: Float2 = (0, 1),
    y_range: Float2 = (0, 1),
    base_layer: LayerSpec = comp_layer,
    slotted_licon: int = 0,
    metal_level: int = 1,
    li_enc_dir="V",
) -> gf.Component:

    """
    return via stack till the metal level indicated where :
    metal_level 1 : till m1
    metal_level 2 : till m2
    metal_level 3 : till m3
    metal_level 4 : till m4
    metal_level 5 : till m5
    withen the range xrange and yrange and expecting the base_layer to be drawen

    """

    c = gf.Component()

    # vias dimensions

    con_size = (0.22, 0.22)
    con_enc = 0.07
    m_enc = 0.06

    # if base_layer == diff_layer or base_layer == tap_layer :
    #     con_enc = (0.06,0.06)

    # #elif  base_layer == tap_layer:
    # #    con_enc = (0.1,0.06)

    # elif base_layer == poly_layer :
    #     con_enc = (0.05,0.08)
    #     npc_enc = 0.01
    #     npc = c.add_ref(gf.components.rectangle(size=(x_range[1]-x_range[0]+2*npc_enc, y_range[1]-y_range[0]+2*npc_enc),layer=npc_layer))
    #     npc.move((x_range[0]-npc_enc, y_range[0]-npc_enc))

    # else :
    #     pass

    con_spacing = (0.28, 0.28)

    via_size = (0.22, 0.22)
    via_spacing = (0.28, 0.28)
    via_enc = (0.06, 0.06)

    if metal_level >= 1:
        con_gen = via_generator(
            x_range=x_range,
            y_range=y_range,
            via_size=con_size,
            via_enclosure=(con_enc, con_enc),
            via_layer=contact_layer,
            via_spacing=con_spacing,
        )
        con = c.add_ref(con_gen)

        m1_x = con.size[0] + 2 * m_enc

        m1_y = con.size[1] + 2 * m_enc

        m1 = c.add_ref(gf.components.rectangle(size=(m1_x, m1_y), layer=m1_layer))
        m1.xmin = con.xmin - m_enc
        m1.ymin = con.ymin - m_enc

    if metal_level >= 2:
        via1_gen = via_generator(
            x_range=(m1.xmin, m1.xmax),
            y_range=(m1.ymin, m1.ymax),
            via_size=via_size,
            via_enclosure=via_enc,
            via_layer=via1_layer,
            via_spacing=via_spacing,
        )
        via1 = c.add_ref(via1_gen)

        if (via1.xmax - via1.xmin + 2 * m_enc[0]) < (
            via_size[0] + 2 * via_enc[0]
        ) and metal_level >= 3:
            m2_x = via_size[0] + 2 * via_enc[0]

        else:
            m2_x = via1.xmax - via1.xmin + 2 * m_enc[0]

        if (via1.ymax - via1.ymin + 2 * m_enc[1]) < (
            via_size[1] + 2 * via_enc[1]
        ) and metal_level >= 3:
            m2_y = via_size[1] + 2 * via_enc[1]

        else:
            m2_y = via1.ymax - via1.ymin + 2 * m_enc[1]

        m2_mx = (m2_x - (via1.xmax - via1.xmin)) / 2
        m2_my = (m2_y - (via1.ymax - via1.ymin)) / 2

        m2 = c.add_ref(gf.components.rectangle(size=(m2_x, m2_y), layer=m2_layer))
        m2.move((via1.xmin - m2_mx, via1.ymin - m2_my))

    return c


# testing the generated methods
if __name__ == "__main__":
    c = via_stack()
    c.show()
    # c = vias_gen_draw(start_layer="li",end_layer="poly")
    # c.show()
