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
# MOS Capacitor Generator for GF180MCU
########################################################################################################################

import pya
from .draw_cap_mos import draw_cap_mos

cap_nmos_w = 1
cap_nmos_l = 1

cap_pmos_w = 1
cap_pmos_l = 1

cap_nmos_b_w = 1
cap_nmos_b_l = 1

cap_pmos_b_w = 1
cap_pmos_b_l = 1

poly_spacing = 0.24


class cap_nmos(pya.PCellDeclarationHelper):
    """
    NMOS capacitor (Outside DNWELL) Generator for GF180MCU
    """

    def __init__(self):

        # Initializing super class.
        super(cap_nmos, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.param("deepnwell", self.TypeBoolean, "Deep NWELL", default=0)
        self.param("pcmpgr", self.TypeBoolean, "Guard Ring", default=0)
        self.Type_handle = self.param("volt", self.TypeList, "Voltage area")
        self.Type_handle.add_choice("3.3V", "3.3V")
        self.Type_handle.add_choice("5/6V", "5/6V")

        self.param("lc", self.TypeDouble, "Length", default=cap_nmos_l, unit="um")
        self.param("wc", self.TypeDouble, "Width", default=cap_nmos_w, unit="um")
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

        self.param("lbl", self.TypeBoolean, "Labels", default=0)

        self.param("g_lbl", self.TypeString, "Gate terminal label", default="")

        self.param("sd_lbl", self.TypeString, "Source/Drain terminal label", default="")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "cap_nmos(LC=" + ("%.3f" % self.lc) + ",WC=" + ("%.3f" % self.wc) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the numeric parameter has changed.
        #  We also update the numerical value or the shape, depending on which on has not changed.
        self.area = self.wc * self.lc
        self.perim = 2 * (self.wc + self.lc)
        # w,l must be larger or equal than min. values.
        if (self.lc) < cap_nmos_l:
            self.lc = cap_nmos_l
        if (self.wc) < cap_nmos_w:
            self.wc = cap_nmos_w

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.layout.dbu / 2
        self.lc = self.layout.get_info(self.lcayer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        np_instance = draw_cap_mos(
            self.layout,
            type="cap_nmos",
            lc=self.lc,
            wc=self.wc,
            volt=self.volt,
            deepnwell=self.deepnwell,
            pcmpgr=self.pcmpgr,
            lbl=self.lbl,
            g_lbl=self.g_lbl,
            sd_lbl=self.sd_lbl,
        )
        write_cells = pya.CellInstArray(
            np_instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )

        self.cell.insert(write_cells)
        self.cell.flatten(1)


class cap_pmos(pya.PCellDeclarationHelper):
    """
    3.3V PMOS capacitor (Outside DNWELL) Generator for GF180MCU
    """

    def __init__(self):

        # Initializing super class.
        super(cap_pmos, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.param("deepnwell", self.TypeBoolean, "Deep NWELL", default=0)
        self.param("pcmpgr", self.TypeBoolean, "Guard Ring", default=0)
        self.Type_handle = self.param("volt", self.TypeList, "Voltage area")
        self.Type_handle.add_choice("3.3V", "3.3V")
        self.Type_handle.add_choice("5/6V", "5/6V")

        self.param("lc", self.TypeDouble, "Length", default=cap_pmos_l, unit="um")
        self.param("wc", self.TypeDouble, "Width", default=cap_pmos_w, unit="um")
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

        self.param("lbl", self.TypeBoolean, "Labels", default=0)

        self.param("g_lbl", self.TypeString, "Gate terminal label", default="")

        self.param("sd_lbl", self.TypeString, "Source/Drain terminal label", default="")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "cap_pmos(LC=" + ("%.3f" % self.lc) + ",WC=" + ("%.3f" % self.wc) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the numeric parameter has changed.
        #  We also update the numerical value or the shape, depending on which on has not changed.
        self.area = self.wc * self.lc
        self.perim = 2 * (self.wc + self.lc)
        # w,l must be larger or equal than min. values.
        if (self.lc) < cap_pmos_l:
            self.lc = cap_pmos_l
        if (self.wc) < cap_pmos_w:
            self.wc = cap_pmos_w

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.layout.dbu / 2
        self.lc = self.layout.get_info(self.lcayer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        np_instance = draw_cap_mos(
            self.layout,
            type="cap_pmos",
            lc=self.lc,
            wc=self.wc,
            volt=self.volt,
            deepnwell=self.deepnwell,
            pcmpgr=self.pcmpgr,
            lbl=self.lbl,
            g_lbl=self.g_lbl,
            sd_lbl=self.sd_lbl,
        )
        write_cells = pya.CellInstArray(
            np_instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )

        self.cell.insert(write_cells)
        self.cell.flatten(1)


class cap_nmos_b(pya.PCellDeclarationHelper):
    """
    3.3V NMOS capacitor (inside NWell) Generator for GF180MCU
    """

    def __init__(self):

        # Initializing super class.
        super(cap_nmos_b, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.Type_handle = self.param("volt", self.TypeList, "Voltage area")
        self.Type_handle.add_choice("3.3V", "3.3V")
        self.Type_handle.add_choice("5/6V", "5/6V")

        self.param("lc", self.TypeDouble, "Length", default=cap_nmos_b_l, unit="um")
        self.param("wc", self.TypeDouble, "Width", default=cap_nmos_b_w, unit="um")
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

        self.param("lbl", self.TypeBoolean, "Labels", default=0)

        self.param("g_lbl", self.TypeString, "Gate terminal label", default="")

        self.param("sd_lbl", self.TypeString, "Source/Drain terminal label", default="")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "cap_nmos_b(LC=" + ("%.3f" % self.lc) + ",WC=" + ("%.3f" % self.wc) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the numeric parameter has changed.
        #  We also update the numerical value or the shape, depending on which on has not changed.
        self.area = self.wc * self.lc
        self.perim = 2 * (self.wc + self.lc)
        # w,l must be larger or equal than min. values.
        if (self.lc) < cap_nmos_b_l:
            self.lc = cap_nmos_b_l
        if (self.wc) < cap_nmos_b_w:
            self.wc = cap_nmos_b_w

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.layout.dbu / 2
        self.lc = self.layout.get_info(self.lcayer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        np_instance = draw_cap_mos(
            self.layout,
            type="cap_nmos_b",
            lc=self.lc,
            wc=self.wc,
            volt=self.volt,
            deepnwell=0,  # self.deepnwell,
            pcmpgr=0,  # self.pcmpgr,
            lbl=self.lbl,
            g_lbl=self.g_lbl,
            sd_lbl=self.sd_lbl,
        )
        write_cells = pya.CellInstArray(
            np_instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )

        self.cell.insert(write_cells)
        self.cell.flatten(1)


class cap_pmos_b(pya.PCellDeclarationHelper):
    """
    3.3V PMOS capacitor (inside Psub) Generator for GF180MCU
    """

    def __init__(self):

        # Initializing super class.
        super(cap_pmos_b, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.Type_handle = self.param("volt", self.TypeList, "Voltage area")
        self.Type_handle.add_choice("3.3V", "3.3V")
        self.Type_handle.add_choice("5/6V", "5/6V")

        self.param("lc", self.TypeDouble, "Length", default=cap_pmos_b_l, unit="um")
        self.param("wc", self.TypeDouble, "Width", default=cap_pmos_b_w, unit="um")
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

        self.param("lbl", self.TypeBoolean, "Labels", default=0)

        self.param("g_lbl", self.TypeString, "Gate terminal label", default="")

        self.param("sd_lbl", self.TypeString, "Source/Drain terminal label", default="")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "cap_pmos_b(LC=" + ("%.3f" % self.lc) + ",WC=" + ("%.3f" % self.wc) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the numeric parameter has changed.
        #  We also update the numerical value or the shape, depending on which on has not changed.
        self.area = self.wc * self.lc
        self.perim = 2 * (self.wc + self.lc)
        # w,l must be larger or equal than min. values.
        if (self.lc) < cap_pmos_b_l:
            self.lc = cap_pmos_b_l
        if (self.wc) < cap_pmos_b_w:
            self.wc = cap_pmos_b_w

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.layout.dbu / 2
        self.lc = self.layout.get_info(self.lcayer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        np_instance = draw_cap_mos(
            self.layout,
            type="cap_pmos_b",
            lc=self.lc,
            wc=self.wc,
            volt=self.volt,
            deepnwell=0,  # self.deepnwell,
            pcmpgr=0,  # self.pcmpgr,
            lbl=self.lbl,
            g_lbl=self.g_lbl,
            sd_lbl=self.sd_lbl,
        )
        write_cells = pya.CellInstArray(
            np_instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )

        self.cell.insert(write_cells)
        self.cell.flatten(1)
