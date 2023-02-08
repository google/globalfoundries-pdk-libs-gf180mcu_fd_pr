"""
Globalfoundries 180u PCells cdl Generator

Usage:
    cdl_gen.py (--help| -h)
    cdl_gen.py (--device=<device_name>) [--thr=<thr>]

Options:
    --help -h                   Print this help message.
    --device=<device_name>      Select your device name. Allowed devices are (bjt , diode, MIM-A, MIM-B_gfB, MIM-B_gfC , fet, cap_mos, res)
    --thr=<thr>                 The number of threads used in run.
"""

import pandas as pd
from docopt import docopt
import os


def cdl_gen(df, device_name):

    cdl_f = open(f"../testcases/{device_name}_pcells.cdl", "w")

    cdl_f.write(
        """
    # Copyright 2022 SkyWater PDK Authors
    #
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #
    #     https://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    #
    # SPDX-License-Identifier: Apache-2.0

    .SUBCKT TOP
        """
    )
    length = df["length"]
    w = df["width"] * df["num_fing"]
    dev = device_name
    interdig = df["interdig"]
    num_fingers = df["num_fing"]
    patt = df["patt"]

    for i in range(len(df)):

        if interdig[i] == 0:

            cdl_f.write(
                f"M{i}_{dev} s{i} g{i} d{i} Sub  {dev} W= {w[i]}u L= {length[i]}u \n   "
            )

        elif int(num_fingers[i]) > 1:

            pat = list(patt[i])
            nt = (
                []
            )  # list to store the symbols of transistors and thier number nt(number of transistors)
            [nt.append(x) for x in pat if x not in nt]
            nl = len(nt)
            u = 0
            for k in range(nl):
                for j in range(len(patt[i])):
                    if patt[i][j] == nt[k]:
                        u += 1
                        g_lbl = f"g{nt[k]}{i}"

                cdl_f.write(
                    f"M{i}_{nt[k]}_{dev} s{i} {g_lbl} d{i} Sub  {dev} W= {round(w[i]*u,2)}u L= {length[i]}u \n   "
                )
                u = 0

    cdl_f.write("\n .ENDS")


if __name__ == "__main__":

    # arguments
    arguments = docopt(__doc__, version="PCELLS Gen.: 0.1")

    device_name = arguments["--device"]

    # No. of threads
    thrCount = (
        os.cpu_count() * 2 if arguments["--thr"] is None else int(arguments["--thr"])
    )

    df = pd.read_csv(f"../patterns/{device_name}_patterns.csv")

    # Calling cdl generation function
    cdl_gen(df=df, device_name=device_name)
