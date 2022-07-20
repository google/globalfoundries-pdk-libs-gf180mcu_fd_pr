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

"""Run GlobalFoundries 180nm MCU FULL LVS Regression.

Usage:
    run_full_regression.py (--help| -h)
    run_full_regression.py [--num_cores=<num>]

Options:
    --help -h              Print this help message.
    --num_cores=<num>      Number of cores to be used by LVS checker
"""
from docopt import docopt
import os


def main():

    # Run Basic LVS Regression
    os.system(f"python3 run_regression.py    --num_cores={workers_count}")

    # Run SC LVS Regression
    os.system(f"python3 run_sc_regression.py --num_cores={workers_count}")


if __name__ == "__main__":

    # Args
    arguments     = docopt(__doc__, version='FULL LVS REGRESSION: 0.1')
    workers_count = os.cpu_count()*2 if arguments["--num_cores"] == None else int(arguments["--num_cores"])

    # Calling main function
    main()
