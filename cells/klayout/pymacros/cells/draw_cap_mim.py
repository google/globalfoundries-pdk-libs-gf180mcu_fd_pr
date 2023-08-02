import gdsfactory as gf

from .via_generator import via_generator, via_stack
from .layers_def import layer
import os


def draw_cap_mim(
    layout,
    mim_option: str = "A",
    metal_level: str = "M4",
    lc: float = 2,
    wc: float = 2,
    lbl: bool = 0,
    top_lbl: str = "",
    bot_lbl: str = "",
):

    """
    Retern mim cap

    Args:
        layout : layout object
        lc : float of cap length
        wc : float of cap width


    """

    c = gf.Component("mim_cap_dev")

    # used dimensions and layers

    # MIM Option selection
    if mim_option == "MIM-A":
        upper_layer = layer["metal3"]
        bottom_layer = layer["metal2"]
        via_layer = layer["via2"]
        up_lbl_layer = layer["metal3_label"]
        bot_lbl_layer = layer["metal2_label"]

    elif mim_option == "MIM-B":
        if metal_level == "M4":
            upper_layer = layer["metal4"]
            bottom_layer = layer["metal3"]
            via_layer = layer["via3"]
            up_lbl_layer = layer["metal4_label"]
            bot_lbl_layer = layer["metal3_label"]
        elif metal_level == "M5":
            upper_layer = layer["metal5"]
            bottom_layer = layer["metal4"]
            via_layer = layer["via4"]
            up_lbl_layer = layer["metal5_label"]
            bot_lbl_layer = layer["metal4_label"]
        elif metal_level == "M6":
            upper_layer = layer["metaltop"]
            bottom_layer = layer["metal5"]
            via_layer = layer["via5"]
            up_lbl_layer = layer["metaltop_label"]
            bot_lbl_layer = layer["metal5_label"]
    else:
        upper_layer = layer["metal3"]
        bottom_layer = layer["metal2"]
        via_layer = layer["via2"]
        up_lbl_layer = layer["metal3_label"]
        bot_lbl_layer = layer["metal2_label"]

    via_size = (0.26, 0.26)
    via_spacing = (0.5, 0.5)
    via_enc = (0.4, 0.4)

    bot_enc_top = 0.6
    l_mk_w = 0.1

    # drawing cap identifier and bottom , upper layers

    m_up = c.add_ref(gf.components.rectangle(size=(wc, lc), layer=upper_layer,))

    fusetop = c.add_ref(
        gf.components.rectangle(
            size=(m_up.size[0], m_up.size[1]), layer=layer["fusetop"]
        )
    )
    fusetop.xmin = m_up.xmin
    fusetop.ymin = m_up.ymin

    mim_l_mk = c.add_ref(
        gf.components.rectangle(size=(fusetop.size[0], l_mk_w), layer=layer["mim_l_mk"])
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
        gf.components.rectangle(
            size=(m_dn.size[0], m_dn.size[1]), layer=layer["cap_mk"]
        )
    )
    cap_mk.xmin = m_dn.xmin
    cap_mk.ymin = m_dn.ymin

    # generating labels
    if lbl == 1:

        c.add_label(
            top_lbl,
            position=(m_up.xmin + (m_up.size[0] / 2), m_dn.xmin + (m_dn.size[1] / 2)),
            layer=up_lbl_layer,
        )

        c.add_label(
            bot_lbl,
            position=(
                m_dn.xmin + (m_dn.size[0] / 2),
                m_dn.ymin + (m_up.ymin - m_dn.ymin) / 2,
            ),
            layer=bot_lbl_layer,
        )

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
    os.remove("mim_cap_temp.gds")

    return layout.cell(cell_name)
