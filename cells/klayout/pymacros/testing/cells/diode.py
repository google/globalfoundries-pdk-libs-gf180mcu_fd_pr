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
# Diode Generator for GF180MCU
########################################################################################################################

import pya
from .draw_diode import *

np_l = 0.36
np_w = 0.22

pn_l = 0.36
pn_w = 0.22

nwp_l = 0.36
nwp_w = 0.22

diode_pw2dw_l = 0.36
diode_pw2dw_w = 0.22

diode_dw2ps_l = 0.36
diode_dw2ps_w = 0.22

sc_l = 1
sc_w = 0.62


class diode_np(pya.PCellDeclarationHelper):
    """
    N+/LVPWELL diode (Outside DNWELL) Generator for GF180MCU
    """

    def __init__(self):

        # Initializing super class.
        super(diode_np, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.param("deepnwell", self.TypeBoolean, "Deep NWELL", default=0)
        self.param("pcmpgr", self.TypeBoolean, "Guard Ring", default=0)
        self.Type_handle = self.param("volt", self.TypeList, "Voltage area")
        self.Type_handle.add_choice("3.3V", "3.3V")
        self.Type_handle.add_choice("5/6V", "5/6V")

        self.param("l", self.TypeDouble, "Length", default=np_l, unit="um")
        self.param("w", self.TypeDouble, "Width", default=np_w, unit="um")
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "diode_np(L=" + ("%.3f" % self.l) + ",W=" + ("%.3f" % self.w) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the numeric parameter has changed.
        #  We also update the numerical value or the shape, depending on which on has not changed.
        self.area = self.w * self.l
        self.perim = 2 * (self.w + self.l)
        # w,l must be larger or equal than min. values.
        if (self.l) < np_l:
            self.l = np_l
        if (self.w) < np_w:
            self.w = np_l

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.layout.dbu / 2
        self.l = self.layout.get_info(self.layer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        np_instance = draw_diode_np(
            self.layout, self.l, self.w, self.volt, self.deepnwell, self.pcmpgr
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


class diode_pn(pya.PCellDeclarationHelper):
    """
    P+/Nwell diode (Outside DNWELL) Generator for GF180MCU
    """

    def __init__(self):

        # Initializing super class.
        super(diode_pn, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.param("deepnwell", self.TypeBoolean, "Deep NWELL", default=0)
        self.param("pcmpgr", self.TypeBoolean, "Guard Ring", default=0)
        self.Type_handle = self.param("volt", self.TypeList, "Voltage area")
        self.Type_handle.add_choice("3.3V", "3.3V")
        self.Type_handle.add_choice("5/6V", "5/6V")

        self.param("l", self.TypeDouble, "Length", default=pn_l, unit="um")
        self.param("w", self.TypeDouble, "Width", default=pn_w, unit="um")
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "diode_pn(L=" + ("%.3f" % self.l) + ",W=" + ("%.3f" % self.w) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the numeric parameter has changed.
        #  We also update the numerical value or the shape, depending on which on has not changed.
        self.area = self.w * self.l
        self.perim = 2 * (self.w + self.l)
        # w,l must be larger or equal than min. values.
        if (self.l) < pn_l:
            self.l = pn_l
        if (self.w) < pn_w:
            self.w = pn_w

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.layout.dbu / 2
        self.l = self.layout.get_info(self.layer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        np_instance = draw_diode_pn(
            self.layout, self.l, self.w, self.volt, self.deepnwell, self.pcmpgr
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


class diode_nw2ps(pya.PCellDeclarationHelper):
    """
    Nwell/Psub diode Generator for GF180MCU
    """

    def __init__(self):

        # Initializing super class.
        super(diode_nw2ps, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.Type_handle = self.param("volt", self.TypeList, "Voltage area")
        self.Type_handle.add_choice("3.3V", "3.3V")
        self.Type_handle.add_choice("5/6V", "5/6V")

        self.param("l", self.TypeDouble, "Length", default=nwp_l, unit="um")
        self.param("w", self.TypeDouble, "Width", default=nwp_w, unit="um")
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "diode_nw2ps(L=" + ("%.3f" % self.l) + ",W=" + ("%.3f" % self.w) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the numeric parameter has changed.
        #  We also update the numerical value or the shape, depending on which on has not changed.
        self.area = self.w * self.l
        self.perim = 2 * (self.w + self.l)
        # w,l must be larger or equal than min. values.
        if (self.l) < nwp_l:
            self.l = nwp_l
        if (self.w) < nwp_w:
            self.w = nwp_w

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.layout.dbu / 2
        self.l = self.layout.get_info(self.layer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        nwp_instance = draw_diode_nw2ps(self.layout, self.l, self.w, self.volt)
        write_cells = pya.CellInstArray(
            nwp_instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )

        self.cell.insert(write_cells)
        self.cell.flatten(1)


class diode_pw2dw(pya.PCellDeclarationHelper):
    """
    LVPWELL/DNWELL diode Generator for GF180MCU
    """

    def __init__(self):

        # Initializing super class.
        super(diode_pw2dw, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.Type_handle = self.param("volt", self.TypeList, "Voltage area")
        self.Type_handle.add_choice("3.3V", "3.3V")
        self.Type_handle.add_choice("5/6V", "5/6V")

        self.param("l", self.TypeDouble, "Length", default=diode_pw2dw_l, unit="um")
        self.param("w", self.TypeDouble, "Width", default=diode_pw2dw_w, unit="um")
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "diode_pw2dw(L=" + ("%.3f" % self.l) + ",W=" + ("%.3f" % self.w) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the numeric parameter has changed.
        #  We also update the numerical value or the shape, depending on which on has not changed.
        self.area = self.w * self.l
        self.perim = 2 * (self.w + self.l)
        # w,l must be larger or equal than min. values.
        if (self.l) < diode_pw2dw_l:
            self.l = diode_pw2dw_l
        if (self.w) < diode_pw2dw_w:
            self.w = diode_pw2dw_w

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.layout.dbu / 2
        self.l = self.layout.get_info(self.layer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        diode_pw2dw_instance = draw_diode_pw2dw(self.layout, self.l, self.w, self.volt)
        write_cells = pya.CellInstArray(
            diode_pw2dw_instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )

        self.cell.insert(write_cells)
        self.cell.flatten(1)


class diode_dw2ps(pya.PCellDeclarationHelper):
    """
    LVPWELL/DNWELL diode Generator for GF180MCU
    """

    def __init__(self):

        # Initializing super class.
        super(diode_dw2ps, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.Type_handle = self.param("volt", self.TypeList, "Voltage area")
        self.Type_handle.add_choice("3.3V", "3.3V")
        self.Type_handle.add_choice("5/6V", "5/6V")

        self.param("l", self.TypeDouble, "Length", default=diode_dw2ps_l, unit="um")
        self.param("w", self.TypeDouble, "Width", default=diode_dw2ps_w, unit="um")
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "diode_dw2ps(L=" + ("%.3f" % self.l) + ",W=" + ("%.3f" % self.w) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the numeric parameter has changed.
        #  We also update the numerical value or the shape, depending on which on has not changed.
        self.area = self.w * self.l
        self.perim = 2 * (self.w + self.l)
        # w,l must be larger or equal than min. values.
        if (self.l) < diode_dw2ps_l:
            self.l = diode_dw2ps_l
        if (self.w) < diode_dw2ps_w:
            self.w = diode_dw2ps_w

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.layout.dbu / 2
        self.l = self.layout.get_info(self.layer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        diode_dw2ps_instance = draw_diode_dw2ps(self.layout, self.l, self.w, self.volt)
        write_cells = pya.CellInstArray(
            diode_dw2ps_instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )

        self.cell.insert(write_cells)
        self.cell.flatten(1)


class sc_diode(pya.PCellDeclarationHelper):
    """
    N+/LVPWELL diode (Outside DNWELL) Generator for GF180MCU
    """

    def __init__(self):

        # Initializing super class.
        super(sc_diode, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.param("pcmpgr", self.TypeBoolean, "Guard Ring", default=0)
        self.param("l", self.TypeDouble, "Length", default=sc_l, unit="um")
        self.param(
            "w", self.TypeDouble, "Width", default=sc_w, unit="um", readonly=True
        )
        self.param("m", self.TypeDouble, "no. of fingers", default=4)
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um^2")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "sc_diode(L=" + ("%.3f" % self.l) + ",W=" + ("%.3f" % self.w) + ")"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the numeric parameter has changed.
        #  We also update the numerical value or the shape, depending on which on has not changed.
        self.area = self.w * self.l
        self.perim = 2 * (self.w + self.l)
        # w,l must be larger or equal than min. values.
        if (self.l) < sc_l:
            self.l = sc_l
        if (self.w) != sc_w:
            self.w = sc_w

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.layout.dbu / 2
        self.l = self.layout.get_info(self.layer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        sc_instance = draw_sc_diode(self.layout, self.l, self.w, self.m, self.pcmpgr)
        write_cells = pya.CellInstArray(
            sc_instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )

        self.cell.insert(write_cells)
        self.cell.flatten(1)
