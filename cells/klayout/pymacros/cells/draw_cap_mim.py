import gdsfactory as gf

from .via_generator import *
from .layers_def import *


def draw_cap_mim(
    layout, mim_option: str = "A", metal_level: str = "M4", l: float = 2, w: float = 2,
):

    """
    Retern mim cap

    Args:
        layout : layout object
        l : float of capm length
        w : float of capm width


    """

    c = gf.Component("mim_cap_dev")

    # used dimensions and layers

    # MIM Option selection
    if mim_option == "MIM-A":
        upper_layer = m3_layer
        bottom_layer = m2_layer
        via_layer = via2_layer

    elif mim_option == "MIM-B":
        if metal_level == "M4":
            upper_layer = m4_layer
            bottom_layer = m3_layer
            via_layer = via3_layer
        elif metal_level == "M5":
            upper_layer = m5_layer
            bottom_layer = m4_layer
            via_layer = via4_layer
        elif metal_level == "M6":
            upper_layer = metaltop_layer
            bottom_layer = m5_layer
            via_layer = via5_layer
    else:
        upper_layer = m3_layer
        bottom_layer = m2_layer
        via_layer = via2_layer

    via_size = (0.22, 0.22)
    via_spacing = (0.5, 0.5)
    via_enc = (0.4, 0.4)

    bot_enc_top = 0.6
    l_mk_w = 0.1

    # drawing cap identifier and bottom , upper layers

    m_up = c.add_ref(gf.components.rectangle(size=(w, l), layer=upper_layer,))

    fusetop = c.add_ref(
        gf.components.rectangle(size=(m_up.size[0], m_up.size[1]), layer=fusetop_layer)
    )
    fusetop.xmin = m_up.xmin
    fusetop.ymin = m_up.ymin

    mim_l_mk = c.add_ref(
        gf.components.rectangle(size=(fusetop.size[0], l_mk_w), layer=mim_l_mk_layer)
    )
    mim_l_mk.xmin = fusetop.xmin
    mim_l_mk.ymin = fusetop.ymin

    m_dn = c.add_ref(
        gf.components.rectangle(
            size=(m_up.size[0] + (2 * bot_enc_top), m_up.size[1] + (2 * bot_enc_top)),
            layer=bottom_layer,
        )
    )
    m_dn.xmin = m_up.xmin - bot_enc_top
    m_dn.ymin = m_up.ymin - bot_enc_top

    cap_mk = c.add_ref(
        gf.components.rectangle(size=(m_dn.size[0], m_dn.size[1]), layer=cap_mk_layer)
    )
    cap_mk.xmin = m_dn.xmin
    cap_mk.ymin = m_dn.ymin

    # generating vias

    via = via_generator(
        x_range=(m_up.xmin, m_up.xmax),
        y_range=(m_up.ymin, m_up.ymax),
        via_enclosure=via_enc,
        via_layer=via_layer,
        via_size=via_size,
        via_spacing=via_spacing,
    )
    c.add_ref(via)

    c.write_gds("mim_cap_temp.gds")
    layout.read("mim_cap_temp.gds")
    cell_name = "mim_cap_dev"

    return layout.cell(cell_name)
