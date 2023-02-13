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
## Pcells cdl Generator for Klayout of GF180MCU
########################################################################################################################

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
import glob



def cdl_gen(df, device_name, device_type):

    cdl_f = open(f"../testcases/{device_name}_pcells.cdl", "w")
    top_cell = df["netlist_name"][0]
    cdl_f.write(
        f"""
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
## {device_name} Pcells cdl Generator for Klayout of GF180MCU
########################################################################################################################

.SUBCKT {top_cell}
        """
    )

    for i,row in df.iterrows():
        nets = row["netlist_nets"].split("_")
        dev_name = row["dev_name"].split("_")
        param = row["netlists_param"].split("_")
        nl = len(nets)
        
        for j in range(nl) : 
            cdl_f.write(
                f"""
{dev_name[j]} {nets[j]} {device_name} {param[j]}
                """
            )
    
    cdl_f.write("""
.ENDS
    """)
    


if __name__ == "__main__":

    # arguments
    arguments = docopt(__doc__, version="PCELLS Gen.: 0.1")

    device = arguments["--device"]

    # No. of threads
    thrCount = (
        os.cpu_count() * 2 if arguments["--thr"] is None else int(arguments["--thr"])
    )

    file_path = os.path.dirname(os.path.abspath(__file__))
    patt_file_path = os.path.dirname(file_path)

    list_patt_files = glob.glob(
        os.path.join(patt_file_path, "patterns", device, "*.csv")
    )

    for p in list_patt_files : 

        device_name = p.split("/")[-1].split("_patt")[0]
        
        # Create output file
        os.makedirs(f"{patt_file_path}/testcases", exist_ok=True)
        out_file = os.path.join(file_path, "testcases", f"{device_name}_pcells.cdl")
        
        df = pd.read_csv(
            f"{patt_file_path}/patterns/{device}/{device_name}_patterns.csv"
        )

        # Calling cdl generation function
        cdl_gen(df=df, device_name=device_name, device_type=device)
