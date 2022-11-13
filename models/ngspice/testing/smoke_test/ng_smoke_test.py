# Copyright 2022 Efabless Corporation
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
"""
Usage:
  smoke_test.py [--num_cores=<num>]

  -h, --help             Show help text.
  -v, --version          Show version.
  --num_cores=<num>      Number of cores to be used by simulator
"""

import re
from docopt import docopt
import pandas as pd 
import os 
from jinja2 import Template
import concurrent.futures
import itertools
import datetime
import warnings
import subprocess

warnings.simplefilter(action='ignore', category=FutureWarning)

def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    p = subprocess.Popen(f"ngspice -b -a {file_name} > {file_name}.log 2>&1", shell=True, executable='/bin/bash')
    p.wait()

def get_sizes(models_path):
    with open(models_path, "r") as f:
        device_model = f.read()
        dimensions = re.findall(f"\.model  nfet_03v3.*\n.*\n\+lmin.*= (.*\S).*\n.*\n\+wmin.*= (.*\S)", device_model)
    return dimensions[0:16]

def get_results(run_path, sizes, temp, corner):
    netlist_tmp = f"./inv_ng.spice"
    width  = float(sizes[1]) * 1000000
    width_p = width * 1.5
    length = float(sizes[0])  * 1000000
    # AD = width * 0.24
    # AD_p = AD * 1.5
    # PD = 2 * (width + 0.24)
    # PD_p = width + PD 
    # AS = AD 
    # PS = PD 
    with open(netlist_tmp) as f:
        tmpl = Template(f.read())

    os.makedirs(f"{run_path}/netlists",exist_ok=True)
    os.makedirs(f"{run_path}/simulation",exist_ok=True)
    netlist_path  = f"{run_path}/netlists/inv_W{width}_L{length}_T{temp}_{corner}.spice"
    with open(netlist_path, "w") as netlist:
        netlist.write(tmpl.render(corner = corner, width = width,length = length, temp = temp , run_path = run_path, width_p = width_p))#, AD = AD , PD = PD , AS = AS , PS = PS, AD_p = AD_p, PD_p = PD_p ))
    
    call_simulator(netlist_path)
    
    # Writing simulated data 
    df_simulated = pd.read_csv(f"{run_path}/simulation/inv_W{width}_L{length}_T{temp}_{corner}.csv",header=None, delimiter=r"\s+")
    return [f"W{width}_L{length}_T{temp}_{corner}",df_simulated.iloc[-1, -1]]  

def main():

    # pandas setup 
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option("max_colwidth", None)
    pd.set_option('display.width', 1000)
            
    models_path = "../../sm141064.ngspice"
    temps = ["25","-40","125"]
    corners = ["typical","ff","ss","fs","sf"]#,"stat"]

    time = f"{datetime.datetime.now()}".replace(" ", "_")
    run_path = f"../run_smoke_{time}"
    os.makedirs(run_path,exist_ok=True)

    sizes = get_sizes(models_path)
    results = []

    all_combs = list(itertools.product(sizes, temps, corners))

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers_count) as executor:
        # Start the load operations and mark each future with its URL
        future_list = [executor.submit(get_results, run_path, comb[0], comb[1], comb[2]) for comb in all_combs]
        for future in concurrent.futures.as_completed(future_list):
            try:
                results.append(future.result())
            except Exception as exc:
                print('Generated an exception: %s' % (exc))


    df_results = pd.DataFrame(results)    
    df_results.columns = ["run","tpd_result"]
    df_results.to_csv(f"{run_path}/final_results.csv",index= False)

    print (df_results)
    

    
# # ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================
        
if __name__ == "__main__":
    
    # Args 
    arguments     = docopt(__doc__, version='smoke_test: 0.1')
    workers_count = os.cpu_count()*2 if arguments["--num_cores"] == None else int(arguments["--num_cores"])
    
    # Calling main function 
    main()
