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
# BJT Generator for GF180MCU
########################################################################################################################

import pya
from .draw_bjt import draw_bjt


class npn_bjt(pya.PCellDeclarationHelper):
    """
    NPN BJT Generator for GF180MCU
    """

    def __init__(self):

        # Important: initialize the super class
        super(npn_bjt, self).__init__()
        self.Type_handle = self.param(
            "Type", self.TypeList, "Type", default="npn_10p00x10p00"
        )
        self.Type_handle.add_choice("npn_10p00x10p00", "npn_10p00x10p00")
        self.Type_handle.add_choice("npn_05p00x05p00", "npn_05p00x05p00")
        self.Type_handle.add_choice("npn_00p54x16p00", "npn_00p54x16p00")
        self.Type_handle.add_choice("npn_00p54x08p00", "npn_00p54x08p00")
        self.Type_handle.add_choice("npn_00p54x04p00", "npn_00p54x04p00")
        self.Type_handle.add_choice("npn_00p54x02p00", "npn_00p54x02p00")
        self.param(
            "Model",
            self.TypeString,
            "Model",
            default="gf180mcu_fd_pr__npn",
            readonly=True,
        )

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return str(self.Type)

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the
        # numeric parameter has changed. We also update the numerical value
        # or the shape, depending on which on has not changed.
        pass

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        pass

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        pass

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        pass

    def produce_impl(self):

        # This is the main part of the implementation: create the layout

        self.percision = 1 / self.layout.dbu
        npn_instance = draw_bjt(layout=self.layout, device_name=self.Type)
        write_cells = pya.CellInstArray(
            npn_instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )

        self.cell.flatten(1)
        self.cell.insert(write_cells)
        self.layout.cleanup()


class pnp_bjt(pya.PCellDeclarationHelper):
    """
    PNP BJT Generator for GF180MCU
    """

    def __init__(self):

        # Important: initialize the super class
        super(pnp_bjt, self).__init__()
        self.Type_handle = self.param(
            "Type", self.TypeList, "Type", default="pnp_10p00x10p00"
        )
        self.Type_handle.add_choice("pnp_10p00x10p00", "pnp_10p00x10p00")
        self.Type_handle.add_choice("pnp_05p00x05p00", "pnp_05p00x05p00")
        self.Type_handle.add_choice("pnp_10p00x00p42", "pnp_10p00x00p42")
        self.Type_handle.add_choice("pnp_05p00x00p42", "pnp_05p00x00p42")
        self.param(
            "Model",
            self.TypeString,
            "Model",
            default="gf180mcu_fd_pr__pnp",
            readonly=True,
        )

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return str(self.Type)

    def coerce_parameters_impl(self):
        # We employ coerce_parameters_impl to decide whether the handle or the
        # numeric parameter has changed. We also update the numerical value
        # or the shape, depending on which on has not changed.
        pass

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which
        # has a finite bounding box
        pass

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's
        # bounding box width and layer
        pass

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's
        # bounding box to determine the transformation
        pass

    def produce_impl(self):

        # This is the main part of the implementation: create the layout

        self.percision = 1 / self.layout.dbu
        pnp_instance = draw_bjt(layout=self.layout, device_name=self.Type)
        write_cells = pya.CellInstArray(
            pnp_instance.cell_index(),
            pya.Trans(pya.Point(0, 0)),
            pya.Vector(0, 0),
            pya.Vector(0, 0),
            1,
            1,
        )

        self.cell.flatten(1)
        self.cell.insert(write_cells)
        self.layout.cleanup()
