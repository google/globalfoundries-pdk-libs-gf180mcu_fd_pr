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
from gdsfactory.typings import Float2, LayerSpec
from .layers_def import layer


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

    nc = floor(width / (via_size[0] + via_spacing[0]))

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
    base_layer: LayerSpec = layer["comp"],
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
    con_enc = 0.08

    con_spacing = (0.29, 0.29)

    via_size = (0.22, 0.22)
    via_spacing = (0.29, 0.29)
    via_enc = (0.07, 0.07)
    m1_area = 0.145

    if metal_level >= 1:
        con_gen = via_generator(
            x_range=x_range,
            y_range=y_range,
            via_size=con_size,
            via_enclosure=(con_enc, con_enc),
            via_layer=layer["contact"],
            via_spacing=con_spacing,
        )
        con = c.add_ref(con_gen)

        m1_x = con.size[0] + 2 * con_enc

        m1_y = con.size[1] + 2 * con_enc

        if (m1_x * m1_y) < m1_area:
            m1_size = (m1_x, round(m1_area / m1_x, 3))
        else:
            m1_size = (m1_x, m1_y)

        m1 = c.add_ref(gf.components.rectangle(size=m1_size, layer=layer["metal1"]))
        m1.center = con.center

    if metal_level >= 2:
        via1_gen = via_generator(
            x_range=(m1.xmin, m1.xmax),
            y_range=(m1.ymin, m1.ymax),
            via_size=via_size,
            via_enclosure=via_enc,
            via_layer=layer["via1"],
            via_spacing=via_spacing,
        )
        via1 = c.add_ref(via1_gen)

        m2 = c.add_ref(
            gf.components.rectangle(
                size=(m1.size[0], m1.size[1]), layer=layer["metal2"]
            )
        )
        m2.center = via1.center

    if metal_level >= 3:
        via2_gen = via_generator(
            x_range=(m2.xmin, m2.xmax),
            y_range=(m2.ymin, m2.ymax),
            via_size=via_size,
            via_enclosure=via_enc,
            via_layer=layer["via2"],
            via_spacing=via_spacing,
        )
        via2 = c.add_ref(via2_gen)

        m3 = c.add_ref(
            gf.components.rectangle(
                size=(m1.size[0], m1.size[1]), layer=layer["metal3"]
            )
        )
        m3.center = via2.center

    if metal_level >= 4:
        via3_gen = via_generator(
            x_range=(m3.xmin, m3.xmax),
            y_range=(m3.ymin, m3.ymax),
            via_size=via_size,
            via_enclosure=via_enc,
            via_layer=layer["via2"],
            via_spacing=via_spacing,
        )
        via3 = c.add_ref(via3_gen)

        m4 = c.add_ref(
            gf.components.rectangle(
                size=(m1.size[0], m1.size[1]), layer=layer["metal4"]
            )
        )
        m4.center = via3.center

    if metal_level >= 5:
        via4_gen = via_generator(
            x_range=(m4.xmin, m4.xmax),
            y_range=(m4.ymin, m4.ymax),
            via_size=via_size,
            via_enclosure=via_enc,
            via_layer=layer["via4"],
            via_spacing=via_spacing,
        )
        via4 = c.add_ref(via4_gen)

        m5 = c.add_ref(
            gf.components.rectangle(
                size=(m1.size[0], m1.size[1]), layer=layer["metal5"]
            )
        )
        m5.center = via4.center

    return c


def get_level_num(base_layer, base_layers, metal_level, metal_layers):
    level_1 = -1
    level_2 = -1

    if base_layer in base_layers:
        level_1 = -1
    else:
        for i in range(len(metal_layers)):
            if base_layer == metal_layers[i]:
                level_1 = i

    if metal_level in base_layers:
        level_2 = -1
    else:
        for i in range(len(metal_layers)):
            if metal_level == metal_layers[i]:
                level_2 = i

    return level_1, level_2


def draw_via_dev(
    layout,
    x_min: float = 0,
    y_min: float = 1,
    x_max: float = 0,
    y_max: float = 1,
    metal_level: str = "M1",
    base_layer: str = "comp",
):

    """

    return via stack till the metal level indicated where :
    metal_level 1 : till m1
    metal_level 2 : till m2
    metal_level 3 : till m3
    metal_level 4 : till m4
    metal_level 5 : till m5
    withen the range xrange and yrange and expecting the base_layer to be drawen

    Args:
        layout : layout object
        x_min :  left x_point of vias generated
        x_max :  right x_point of vias generated
        y_min :  bottom y_point of vias generated
        y_max :  top y_point of vias generated

    """

    c = gf.Component("via_stack_dev")

    # vias dimensions

    x_range = x_max - x_min
    y_range = y_max - y_min

    con_size = (0.22, 0.22)
    con_enc = (0.08, 0.08)

    con_spacing = (0.26, 0.26)

    via_size = (0.26, 0.26)
    via_spacing = (0.27, 0.27)

    if x_range > (4 * con_size[0] + 3 * con_spacing[0]) and y_range > (
        2 * 4 * via_size[1] + 3 * via_spacing[1]
    ):
        con_spacing = (0.28, 0.28)

    if x_range > (4 * via_size[0] + 3 * via_spacing[0]) and y_range > (
        4 * via_size[1] + 3 * via_spacing[1]
    ):
        via_spacing = (0.36, 0.36)

    via_enc = (0.06, 0.06)

    base_layers = ["poly2", "comp"]
    metal_layers = ["M1", "M2", "M3", "M4", "M5", "Mtop"]

    level_1, level_2 = get_level_num(base_layer, base_layers, metal_level, metal_layers)

    if level_1 <= -1 and level_2 >= -1 and base_layer in layer:
        c.add_ref(
            gf.components.rectangle(size=(x_range, y_range), layer=layer[base_layer])
        )

        if level_2 == -1 and metal_level in layer:
            c.add_ref(
                gf.components.rectangle(
                    size=(x_range, y_range), layer=layer[metal_level]
                )
            )

    if level_1 <= 0 and level_2 >= 0:
        c.add_ref(
            gf.components.rectangle(size=(x_range, y_range), layer=layer["metal1"])
        )

    if level_1 <= 1 and level_2 >= 1:
        c.add_ref(
            gf.components.rectangle(size=(x_range, y_range), layer=layer["metal2"])
        )

    if level_1 <= 2 and level_2 >= 2:
        c.add_ref(
            gf.components.rectangle(size=(x_range, y_range), layer=layer["metal3"])
        )

    if level_1 <= 3 and level_2 >= 3:
        c.add_ref(
            gf.components.rectangle(size=(x_range, y_range), layer=layer["metal4"])
        )

    if level_1 <= 4 and level_2 >= 4:
        c.add_ref(
            gf.components.rectangle(size=(x_range, y_range), layer=layer["metal5"])
        )

    if level_1 <= 5 and level_2 >= 5:
        c.add_ref(
            gf.components.rectangle(size=(x_range, y_range), layer=layer["metaltop"])
        )

    if level_1 <= -1 and level_2 > -1:
        con = via_generator(
            x_range=(x_min, x_max),
            y_range=(y_min, y_max),
            via_size=con_size,
            via_layer=layer["contact"],
            via_enclosure=con_enc,
            via_spacing=con_spacing,
        )
        c.add_ref(con)

    if level_1 <= 0 and level_2 > 0:
        v1 = via_generator(
            x_range=(x_min, x_max),
            y_range=(y_min, y_max),
            via_size=via_size,
            via_layer=layer["via1"],
            via_enclosure=via_enc,
            via_spacing=via_spacing,
        )
        c.add_ref(v1)

    if level_1 <= 1 and level_2 > 1:
        v2 = via_generator(
            x_range=(x_min, x_max),
            y_range=(y_min, y_max),
            via_size=via_size,
            via_layer=layer["via2"],
            via_enclosure=via_enc,
            via_spacing=via_spacing,
        )
        c.add_ref(v2)

    if level_1 <= 2 and level_2 > 2:
        v3 = via_generator(
            x_range=(x_min, x_max),
            y_range=(y_min, y_max),
            via_size=via_size,
            via_layer=layer["via3"],
            via_enclosure=via_enc,
            via_spacing=via_spacing,
        )
        c.add_ref(v3)

    if level_1 <= 3 and level_2 > 3:
        v4 = via_generator(
            x_range=(x_min, x_max),
            y_range=(y_min, y_max),
            via_size=via_size,
            via_layer=layer["via4"],
            via_enclosure=via_enc,
            via_spacing=via_spacing,
        )
        c.add_ref(v4)

    if level_1 <= 4 and level_2 > 4:
        v5 = via_generator(
            x_range=(x_min, x_max),
            y_range=(y_min, y_max),
            via_size=via_size,
            via_layer=layer["via5"],
            via_enclosure=via_enc,
            via_spacing=via_spacing,
        )
        c.add_ref(v5)

    c.write_gds("via_stack_temp.gds")
    layout.read("via_stack_temp.gds")
    cell_name = "via_stack_dev"
    print(type(layout.cell(cell_name)))

    return layout.cell(cell_name)


# testing the generated methods
if __name__ == "__main__":
    c = via_stack()
    c.show()
    # c = vias_gen_draw(base_layer="li",end_layer="poly")
    # c.show()
