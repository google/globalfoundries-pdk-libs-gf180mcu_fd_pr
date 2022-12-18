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

import glob
import subprocess
from datetime import datetime
import xml.etree.ElementTree as ET

gds_files = glob.glob("testcases/*.gds")
current = f'run_{datetime.now().strftime("_%y_%m_%d_%H_%M_%S")}'
subprocess.check_call(f"mkdir {current}", shell=True)

for gds_file in gds_files:
    txt_file = gds_file.replace(".gds", ".txt").replace("testcases", current)
    out_file = gds_file.replace(".gds", "_o.gds").replace("testcases", current)
    rep_file = gds_file.replace(".gds", "_r.gds").replace("testcases", current)
    subprocess.check_call(f"gds2txt {gds_file} > {txt_file}", shell=True)
    subprocess.check_call(f"txt2gds -o {out_file} {txt_file}", shell=True)
    subprocess.check_call(
        f"klayout -b -r xor.drc -rd gds1={gds_file} -rd gds2={out_file} -rd out={rep_file}",
        shell=True,
    )
    subprocess.check_call(f"klayout -b -r report.drc -rd input={rep_file}", shell=True)

    mytree = ET.parse(
        f'{gds_file.replace(".gds", "").replace("testcases", current)}_xor.lyrdb'
    )
    myroot = mytree.getroot()
    if len(myroot[7]) == 0:
        print(
            f'## File {gds_file.replace(".gds", "").replace("testcases/", "")} has been converted as GDS > TXT > GDS successfully'
        )

subprocess.check_call(f"rm report.drc", shell=True)
print("\x1b[6;30;42m" + "Success!" + "\x1b[0m")
