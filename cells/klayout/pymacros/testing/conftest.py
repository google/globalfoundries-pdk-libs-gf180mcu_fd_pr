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
## Pcells Generators regression variables setup for Klayout of GF180MCU
########################################################################################################################


import os
import glob
from subprocess import check_call


def pytest_addoption(parser):
    """
    assign parameter to be passed from command line

    Args:
        parser : pytest built in fixture that parse information from command line
    """
    parser.addoption(
        "--device", action="store", default="fet", help="device under test name"
    )


def pytest_generate_tests(metafunc):
    """
    generates parametrized test setup

    Args :
        metafunc : pytest built in fixture that read data for test functions
    """
    if "device_name" in metafunc.fixturenames:
        dev = metafunc.config.getoption("device")

        devices = []

        # get patterns directory
        dir_path = os.path.dirname((os.path.abspath(__file__)))
        list_patt_files = glob.glob(os.path.join(dir_path, "patterns", dev, "*.csv"))

        # create devices_name list
        for file_path in list_patt_files:
            devices.append(file_path.split("/")[-1].split("_patt")[0])

        # make parametric testing of devices list
        metafunc.parametrize("device_name", devices)
