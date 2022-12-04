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


"""Run GDS/TXT converter.

Usage:
    gds_convert.py (--help| -h)
    gds_convert.py (--gds=<layout_path>) (--mode=<mode>) (--txt=<txt_path>)

Options:
    --help -h                            Print this help message.
    --gds=<gds_path>                     The input GDS file path.
    --mode=<mode>                        The operation mode (to, form).
    --txt=<txt_path>                     The input text file path.
"""

from docopt import docopt
import subprocess


def main():
    if args["--gds"]:
        gds = args["--gds"]
        if args["--txt"]:
            txt = args["--txt"]
        else:
            print(
                "The script must be given a txt file or a path to be able to run conversion"
            )
            exit()
    else:
        print(
            "The script must be given a gds file or a path to be able to run conversion"
        )
        exit()

    if args["--mode"] == "to":
        subprocess.check_call(f"gds2txt {gds} > {txt}", shell=True)
    elif args["--mode"] == "from":
        subprocess.check_call(f"txt2gds -o {gds} {txt}", shell=True)
    else:
        print(
            "The script must be given a mode operation ['to', 'from'] only to be able to run conversion"
        )
        exit()


if __name__ == "__main__":

    # Args
    args = docopt(__doc__, version="GDS/TXT converter: 0.1")
    main()
