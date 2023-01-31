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
## BJT Pcells Generators for Klayout of GF180MCU
########################################################################################################################

import os

gds_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bjt")


def draw_bjt(layout, device_name):

    gds_file = f"{gds_path}/{device_name}.gds"

    if os.path.exists(gds_file) and os.path.isfile(gds_file):
        layout.read(gds_file)
    else:
        print(f"{gds_file} is not exist, please recheck")

    return layout.cell(device_name)
