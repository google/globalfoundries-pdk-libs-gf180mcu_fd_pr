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
# MIM Capacitor Generator for GF180MCU
########################################################################################################################

import pya
import os
from .via_generator import draw_via_dev

via_size = 0.26
via_enc = 0.07
mt_min = 0.75


class via_dev(pya.PCellDeclarationHelper):
    """
    Via Generator for GF180MCU
    """

    def __init__(self):

        # Initializing super class.
        super(via_dev, self).__init__()

        # ===================== PARAMETERS DECLARATIONS =====================
        self.Type_handle = self.param("base_layer", self.TypeList, "start_layer")
        self.Type_handle.add_choice("poly2", "poly2")
        self.Type_handle.add_choice("comp", "comp")
        self.Type_handle.add_choice("M1", "M1")
        self.Type_handle.add_choice("M2", "M2")
        self.Type_handle.add_choice("M3", "M3")
        self.Type_handle.add_choice("M4", "M4")
        self.Type_handle.add_choice("M5", "M5")
        self.Type_handle.add_choice("Mtop", "Mtop")

        self.Type_handle = self.param("metal_level", self.TypeList, "end_layer")
        self.Type_handle.add_choice("poly2", "poly2")
        self.Type_handle.add_choice("comp", "comp")
        self.Type_handle.add_choice("M1", "M1")
        self.Type_handle.add_choice("M2", "M2")
        self.Type_handle.add_choice("M3", "M3")
        self.Type_handle.add_choice("M4", "M4")
        self.Type_handle.add_choice("M5", "M5")
        self.Type_handle.add_choice("Mtop", "Mtop")

        self.param("x_min", self.TypeDouble, "X_min", default=0, unit="um")
        self.param("y_min", self.TypeDouble, "Y_min", default=0, unit="um")
        self.param("x_max", self.TypeDouble, "X_max", default=1, unit="um")
        self.param("y_max", self.TypeDouble, "Y_max", default=1, unit="um")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "via_stack"

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the numeric parameter has changed.
        #  We also update the numerical value or the shape, depending on which on has not changed.

        if self.metal_level == "Mtop":
            if (self.x_max - self.x_min) < mt_min:
                self.x_max = self.x_min + mt_min

            if (self.y_max - self.y_min) < mt_min:
                self.y_max = self.y_min + mt_min

        else:
            if (self.x_max - self.x_min) < (via_size + (2 * via_enc)):
                self.x_max = self.x_min + (via_size + (2 * via_enc))

            if (self.y_max - self.y_min) < (via_size + (2 * via_enc)):
                self.y_max = self.y_min + (via_size + (2 * via_enc))

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        self.r = self.shape.bbox().width() * self.layout.dbu / 2
        self.lc = self.layout.get_info(self.layer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        np_instance = draw_via_dev(
            self.layout,
            x_min=self.x_min,
            y_min=self.y_min,
            x_max=self.x_max,
            y_max=self.y_max,
            metal_level=self.metal_level,
            base_layer=self.base_layer,
        )
        print(type(np_instance))
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
