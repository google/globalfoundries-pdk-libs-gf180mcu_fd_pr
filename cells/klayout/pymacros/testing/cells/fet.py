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
# FET Generator for GF180MCU
########################################################################################################################
import pya
from .draw_fet import (
    draw_nfet,
    draw_pfet,
    draw_nfet_10v0_asym,
    draw_nfet_06v0_nvt,
    draw_pfet_10v0_asym,
)

fet_3p3_l = 0.28
fet_3p3_w = 0.22
fet_5_6_w = 0.3

nfet_05v0_l = 0.6
nfet_06v0_l = 0.7

pfet_05v0_l = 0.5
pfet_06v0_l = 0.55

nfet_nat_l = 1.8
nfet_nat_w = 0.8
fet_grw = 0.36
fet_ld = 0.44

ldfet_l_min = 0.6
ldfet_l_max = 20
ldfet_w_min = 4
ldfet_w_max = 50


class nfet(pya.PCellDeclarationHelper):
    """
    NFET Generator for GF180MCU
    """

    def __init__(self):
        # Initialize super class.
        super(nfet, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.param("deepnwell", self.TypeBoolean, "Deep NWELL", default=0)
        self.param("pcmpgr", self.TypeBoolean, "Deep NWELL Guard Ring", default=0)
        self.Type_handle = self.param("volt", self.TypeList, "Operating Voltage")
        self.Type_handle.add_choice("3.3V", "3.3V")
        self.Type_handle.add_choice("5V", "5V")
        self.Type_handle.add_choice("6V", "6V")
        self.Type_handle = self.param("bulk", self.TypeList, "Bulk Type")
        self.Type_handle.add_choice("None", "None")
        self.Type_handle.add_choice("Bulk Tie", "Bulk Tie")
        self.Type_handle.add_choice("Guard Ring", "Guard Ring")

        self.param("w", self.TypeDouble, "Width", default=fet_3p3_w, unit="um")
        self.param("l_gate", self.TypeDouble, "Length", default=fet_3p3_l, unit="um")
        self.param("ld", self.TypeDouble, "Diffusion Length", default=fet_ld, unit="um")
        self.param("nf", self.TypeInt, "Number of Fingers", default=1)
        self.param(
            "grw", self.TypeDouble, "Guard Ring Width", default=fet_grw, unit="um"
        )
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "nfet(L=" + ("%.3f" % self.l_gate) + ",W=" + ("%.3f" % self.w) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the
        # numeric parameter has changed (by comparing against the effective
        # radius ru) and set ru to the effective radius. We also update the
        # numerical value or the shape, depending on which on has not changed.
        self.area = self.w * self.l_gate
        self.perim = 2 * (self.w + self.l_gate)
        # w,l must be larger or equal than min. values.
        if self.volt == "3.3V":
            if (self.l_gate) < fet_3p3_l:
                self.l_gate = fet_3p3_l
            if (self.w) < fet_3p3_w:
                self.w = fet_3p3_w
        elif self.volt == "5V":
            if (self.l_gate) < nfet_05v0_l:
                self.l_gate = nfet_05v0_l
            if (self.w) < fet_5_6_w:
                self.w = fet_5_6_w
        elif self.volt == "6V":
            if (self.l_gate) < nfet_06v0_l:
                self.l_gate = nfet_06v0_l
            if (self.w) < fet_5_6_w:
                self.w = fet_5_6_w

        if (self.l_gated) < fet_ld:
            self.l_gated = fet_ld

        if (self.grw) < fet_grw:
            self.grw = fet_grw

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.l_gateayout.dbu / 2
        self.l_gate = self.l_gateayout.get_info(self.l_gateayer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        instance = draw_nfet(
            self.l_gateayout,
            self.l_gate,
            self.w,
            self.l_gated,
            self.nf,
            self.grw,
            self.bulk,
            self.volt,
            self.deepnwell,
            self.pcmpgr,
        )
        write_cells = pya.CellInstArray(
            instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )
        self.cell.insert(write_cells)
        self.cell.flatten(1)


class pfet(pya.PCellDeclarationHelper):
    """
    PFET Generator for GF180MCU
    """

    def __init__(self):
        # Initialize super class.
        super(pfet, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.param("deepnwell", self.TypeBoolean, "Deep NWELL", default=0)
        self.param("pcmpgr", self.TypeBoolean, "Deep NWELL Guard Ring", default=0)
        self.Type_handle = self.param("volt", self.TypeList, "Voltage area")
        self.Type_handle.add_choice("3.3V", "3.3V")
        self.Type_handle.add_choice("5V", "5V")
        self.Type_handle.add_choice("6V", "6V")
        self.Type_handle = self.param("bulk", self.TypeList, "Bulk Type")
        self.Type_handle.add_choice("None", "None")
        self.Type_handle.add_choice("Bulk Tie", "Bulk Tie")
        self.Type_handle.add_choice("Guard Ring", "Guard Ring")

        self.param("w", self.TypeDouble, "Width", default=fet_3p3_w, unit="um")
        self.param("l_gate", self.TypeDouble, "Length", default=fet_3p3_l, unit="um")
        self.param("ld", self.TypeDouble, "Diffusion Length", default=fet_ld, unit="um")
        self.param("nf", self.TypeInt, "Number of Fingers", default=1)
        self.param(
            "grw", self.TypeDouble, "Guard Ring Width", default=fet_grw, unit="um"
        )
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "pfet(L=" + ("%.3f" % self.l_gate) + ",W=" + ("%.3f" % self.w) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the
        # numeric parameter has changed (by comparing against the effective
        # radius ru) and set ru to the effective radius. We also update the
        # numerical value or the shape, depending on which on has not changed.
        self.area = self.w * self.l_gate
        self.perim = 2 * (self.w + self.l_gate)
        # w,l must be larger or equal than min. values.
        if self.volt == "3.3V":
            if (self.l_gate) < fet_3p3_l:
                self.l_gate = fet_3p3_l
            if (self.w) < fet_3p3_w:
                self.w = fet_3p3_w
        elif self.volt == "5V":
            if (self.l_gate) < pfet_05v0_l:
                self.l_gate = pfet_05v0_l
            if (self.w) < fet_5_6_w:
                self.w = fet_5_6_w
        elif self.volt == "6V":
            if (self.l_gate) < pfet_06v0_l:
                self.l_gate = pfet_06v0_l
            if (self.w) < fet_5_6_w:
                self.w = fet_5_6_w

        if (self.l_gated) < fet_ld:
            self.l_gated = fet_ld

        if (self.grw) < fet_grw:
            self.grw = fet_grw

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.l_gateayout.dbu / 2
        self.l_gate = self.l_gateayout.get_info(self.l_gateayer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        instance = draw_pfet(
            self.l_gateayout,
            self.l_gate,
            self.w,
            self.l_gated,
            self.nf,
            self.grw,
            self.bulk,
            self.volt,
            self.deepnwell,
            self.pcmpgr,
        )
        write_cells = pya.CellInstArray(
            instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )
        self.cell.insert(write_cells)
        self.cell.flatten(1)


class nfet_06v0_nvt(pya.PCellDeclarationHelper):
    """
    6V Native NFET Generator for GF180MCU
    """

    def __init__(self):
        # Initialize super class.
        super(nfet_06v0_nvt, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.Type_handle = self.param("bulk", self.TypeList, "Bulk Type")
        self.Type_handle.add_choice("None", "None")
        self.Type_handle.add_choice("Bulk Tie", "Bulk Tie")
        self.Type_handle.add_choice("Guard Ring", "Guard Ring")

        self.param("w", self.TypeDouble, "Width", default=nfet_nat_w, unit="um")
        self.param("l_gate", self.TypeDouble, "Length", default=nfet_nat_l, unit="um")
        self.param("ld", self.TypeDouble, "Diffusion Length", default=fet_ld, unit="um")
        self.param("nf", self.TypeInt, "Number of Fingers", default=1)
        self.param(
            "grw", self.TypeDouble, "Guard Ring Width", default=fet_grw, unit="um"
        )
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "nfet_06v0_nvt(L=" + ("%.3f" % self.l_gate) + ",W=" + ("%.3f" % self.w) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the
        # numeric parameter has changed (by comparing against the effective
        # radius ru) and set ru to the effective radius. We also update the
        # numerical value or the shape, depending on which on has not changed.
        self.area = self.w * self.l_gate
        self.perim = 2 * (self.w + self.l_gate)
        # w,l must be larger or equal than min. values.
        if (self.l_gate) < nfet_nat_l:
            self.l_gate = nfet_nat_l

        if (self.w) < nfet_nat_w:
            self.w = nfet_nat_w

        if (self.grw) < fet_grw:
            self.grw = fet_grw

        if (self.l_gated) < fet_ld:
            self.l_gated = fet_ld

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.l_gateayout.dbu / 2
        self.l_gate = self.l_gateayout.get_info(self.l_gateayer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        instance = draw_nfet_06v0_nvt(
            self.l_gateayout, self.l_gate, self.w, self.l_gated, self.nf, self.grw, self.bulk
        )
        write_cells = pya.CellInstArray(
            instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )
        self.cell.insert(write_cells)
        self.cell.flatten(1)


class nfet_10v0_asym(pya.PCellDeclarationHelper):
    """
    10V LDNFET Generator for GF180MCU
    """

    def __init__(self):
        # Initialize super class.
        super(nfet_10v0_asym, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================

        self.param("w", self.TypeDouble, "Width", default=ldfet_w_min, unit="um")
        self.param("l_gate", self.TypeDouble, "Length", default=ldfet_l_min, unit="um")
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "nfet_10v0_asym(L=" + ("%.3f" % self.l_gate) + ",W=" + ("%.3f" % self.w) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the
        # numeric parameter has changed (by comparing against the effective
        # radius ru) and set ru to the effective radius. We also update the
        # numerical value or the shape, depending on which on has not changed.
        self.area = self.w * self.l_gate
        self.perim = 2 * (self.w + self.l_gate)
        # w,l must be larger or equal than min. values.
        if (self.l_gate) < ldfet_l_min:
            self.l_gate = ldfet_l_min
        if (self.l_gate) > ldfet_l_max:
            self.l_gate = ldfet_l_max
        if (self.w) < ldfet_w_min:
            self.w = ldfet_w_min
        if (self.w) > ldfet_w_max:
            self.w = ldfet_w_max

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.l_gateayout.dbu / 2
        self.l_gate = self.l_gateayout.get_info(self.l_gateayer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        instance = draw_nfet_10v0_asym(self.l_gateayout, self.l_gate, self.w)
        write_cells = pya.CellInstArray(
            instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )
        self.cell.insert(write_cells)
        self.cell.flatten(1)


class pfet_10v0_asym(pya.PCellDeclarationHelper):
    """
    10V LDPFET Generator for GF180MCU
    """

    def __init__(self):
        # Initialize super class.
        super(pfet_10v0_asym, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================

        self.param("w", self.TypeDouble, "Width", default=ldfet_w_min, unit="um")
        self.param("l_gate", self.TypeDouble, "Length", default=ldfet_l_min, unit="um")
        self.param("double_gr", self.TypeBoolean, "Double Guard Ring", default=1)
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "pfet_10v0_asym(L=" + ("%.3f" % self.l_gate) + ",W=" + ("%.3f" % self.w) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the
        # numeric parameter has changed (by comparing against the effective
        # radius ru) and set ru to the effective radius. We also update the
        # numerical value or the shape, depending on which on has not changed.
        self.area = self.w * self.l_gate
        self.perim = 2 * (self.w + self.l_gate)
        # w,l must be larger or equal than min. values.
        if (self.l_gate) < ldfet_l_min:
            self.l_gate = ldfet_l_min
        if (self.l_gate) > ldfet_l_max:
            self.l_gate = ldfet_l_max
        if (self.w) < ldfet_w_min:
            self.w = ldfet_w_min
        if (self.w) > ldfet_w_max:
            self.w = ldfet_w_max

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.l_gateayout.dbu / 2
        self.l_gate = self.l_gateayout.get_info(self.l_gateayer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        instance = draw_pfet_10v0_asym(self.l_gateayout, self.l_gate, self.w, self.double_gr)
        write_cells = pya.CellInstArray(
            instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )
        self.cell.insert(write_cells)
        self.cell.flatten(1)
