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

"""Run GlobalFoundries 180nm MCU SC LVS Regression.

Usage: 
    run_sc_regression.py (--help| -h)
    run_sc_regression.py (--run_dir=<run_dir>) [--num_cores=<num>]

Options:
    --help -h              Print this help message.
    --run_dir=<run_dir>    Selecting your output path.    
    --num_cores=<num>      Number of cores to be used by LVS checker 
"""

from docopt import docopt
import os
import concurrent.futures
import glob
import shutil
import re
import pandas as pd 
import numpy as np
import time
import logging

def lvs_check(sc_input):

    # print(f"================================================")
    # print ('{:-^48}'.format(sc_input.upper()))
    # print(f"================================================ \n")
    
    # Selecting correct netlist 
    if "gf180mcu_fd_io_" in sc_input:
        cdl_input = sc_input[:-4]
        cdl_input_clean = cdl_input.split("/")[-1]
    else: 
        cdl_input = sc_input
        cdl_input_clean = sc_input.split("/")[-1]

    if "sc" in sc_input:
        sc_input_clean  = sc_input.split ("/")[-1]
        cdl_input = f"sc_netlists/{sc_input_clean}"

    # Cleaning netlist [Remove unnecessary chars] and writing it again
    unnecessary_chars = ["$SUB=" ,"$[" , "]"]
         
    if "sc" in sc_input and "io" not in sc_input:
        
        with open(f'sc_testcases/sc_split/{cdl_input}.cdl', 'r') as file :
            spice_netlist = file.read()
        for char in unnecessary_chars:
            spice_netlist = spice_netlist.replace(char, '')

        with open(f'sc_testcases/sc_split/{cdl_input}_modified.cdl', 'w') as file:
            file.write(spice_netlist)
        
        cdl_input_clean = cdl_input
    else:
        with open(f'sc_testcases/{cdl_input}.cdl', 'r') as file :
            spice_netlist = file.read()
        for char in unnecessary_chars:
            spice_netlist = spice_netlist.replace(char, '')

        with open(f'sc_testcases/{cdl_input}_modified.cdl', 'w') as file:
            file.write(spice_netlist)
        
    sc_input_clean = sc_input.split("/")[-1]

    # Running LVS
    result = os.popen(f"klayout -b -r ../gf180mcu.lvs -rd input=sc_testcases/{sc_input}.gds -rd report={sc_input_clean}.lvsdb -rd schematic={cdl_input_clean}_modified.cdl -rd thr={workers_count} -rd schematic_simplify=true").read()
    

    # moving all reports to run dir
    out_dir = arguments["--run_dir"]
    # os.system(f"cd {out_dir} && mkdir {sc_input_clean}")
    # os.system(f"mv -f sc_testcases/{sc_input}.lvsdb sc_testcases/*/{cdl_input_clean}_extracted.cir sc_testcases/*/{cdl_input_clean}_modified.cdl {out_dir}/{sc_input_clean}/")
        
    if "INFO : Congratulations! Netlists match." in result:
        logging.info(f"Extraction of {sc_input_clean} is passed")
        
        with open ("sc_testcases/sc_report.csv","a+") as rep:
            rep.write(f"{sc_input_clean},passed\n")
    else:
        logging.info(f"Extraction of {sc_input_clean} is failed")        

        with open ("sc_testcases/sc_report.csv","a+") as rep:
            rep.write(f"{sc_input_clean},failed\n")

def main():
        
    # Remove old report 
    os.system(f"rm -rf sc_testcases/sc_report.csv")
         
    # cell_list = ["GF018_5VGreen_SRAM_1P_64x8M8WM1" , "GF018_5VGreen_SRAM_1P_128x8M8WM1" , "GF018_5VGreen_SRAM_1P_256x8M8WM1" , "GF018_5VGreen_SRAM_1P_512x8M8WM1" ,
    #            "GF018green_ipio_5p0c_75_3lm"     , "GF018green_ipio_5p0c_75_4lm"      , "GF018green_ipio_5p0c_75_5lm"      ,
    #            "GF018hv5v_mcu_sc7"               , "GF018hv5v_green_sc9" ] 
    
    cell_list = [ "gf180mcu_fd_io_3lm"     , "gf180mcu_fd_io_4lm"  , "gf180mcu_fd_io_5lm",
                  "GF018hv5v_mcu_sc7"      , "GF018hv5v_green_sc9" ] 
    
    # Create GDS splitter script
    if os.path.exists("sc_testcases/sc_split") and os.path.isdir("sc_testcases/sc_split"):
            shutil.rmtree("sc_testcases/sc_split")
    with open('sc_testcases/split_gds.rb', 'w') as f:
        f.write(''' layout = RBA::Layout::new
                    layout.read($input)
                    Dir.mkdir("sc_testcases/sc_split") unless File.exists?("sc_testcases/sc_split")

                    layout.each_cell do |cell|
                        ly2 = RBA::Layout.new
                        ly2.dbu = layout.dbu
                        cell_index = layout.cell_by_name("#{cell.name}")
                        new_top = ly2.add_cell("#{cell.name}") 
                        ly2.cell(new_top).copy_tree(layout.cell("#{cell.name}"))
                        ly2.write("sc_testcases/sc_split/#{cell.name}.gds")
                    end''')

    # Split standard cells top-cells into multiple gds files
    for cell in cell_list:
        if "sc" in cell:
            os.system(f"klayout -b -r sc_testcases/split_gds.rb -rd input=sc_testcases/{cell}.gds")
    os.system(f"rm -rf sc_testcases/split_gds.rb")
            
    # Create cdl splitter script
    sc_cdl = ["GF018hv5v_mcu_sc7" , "GF018hv5v_green_sc9"]
    sc_result = []
    get_line = False
    os.makedirs(f"sc_testcases/sc_split/sc_netlists/",exist_ok=False)
    
    for cdl in sc_cdl:          
        with open(f'sc_testcases/{cdl}.cdl', 'r') as cdl1:
            for line in cdl1:
                if ".SUBCKT" in line:
                    get_line = True
                    sc_result = []            
                if get_line:
                    sc_result.append(line)                
                if '.ENDS' in line:
                    get_line = False
                    name = re.findall('.SUBCKT (\w+)', sc_result[0])                    
                    with open(f"sc_testcases/sc_split/sc_netlists/{name[0]}.cdl", 'w') as out_cdl:
                        out_cdl.write(''.join(sc_result))


    with concurrent.futures.ProcessPoolExecutor(max_workers=workers_count) as executor:
        for cell in cell_list:
            # Split standard cells top-cells into multiple gds files
            if "sc" not in cell:
                if "io" in cell:
                    cells_splitted = glob.glob(f"sc_testcases/{cell}/*.gds")
                    for cell_split in cells_splitted:
                        cell_split_clean = cell_split.replace(".gds","").replace("sc_testcases/","")
                        executor.submit(lvs_check, cell_split_clean)                    
                else:
                    executor.submit(lvs_check, cell)
            
        # Running LVS on SC
        sc_list = glob.glob("sc_testcases/sc_split/*")
        for sc in sc_list: 
            sc_clean = sc.split ('.gds')[0]            
            sc_clean = sc_clean.split ('sc_testcases/')[-1]           
            executor.submit(lvs_check, sc_clean)
            
    df = pd.read_csv("sc_testcases/sc_report.csv")
    df.columns = ["CELL NAME","RESULT"]
    df.to_csv("sc_testcases/sc_report.csv", index = False)
    
       
if __name__ == "__main__":

    # logs format 
    logging.basicConfig(level=logging.DEBUG, format=f"%(asctime)s | %(levelname)-7s | %(message)s", datefmt='%d-%b-%Y %H:%M:%S')
    
    # Args 
    arguments     = docopt(__doc__, version='SC LVS REGRESSION: 0.1')
    workers_count = os.cpu_count()*2 if arguments["--num_cores"] == None else int(arguments["--num_cores"])
    
    out_dir = arguments["--run_dir"]
    # Check out_dir existance 
    if os.path.exists(out_dir) and os.path.isdir(out_dir):
        pass
    else:
        logging.error("This run directory doesn't exist. Please recheck.")
        exit ()
        
    pass_count = 0
    fail_count = 0
        
    # Calling main function 
    main()
    
    time.sleep(10)

    df = pd.read_csv("sc_testcases/sc_report.csv")
    pass_count = df["RESULT"].str.count("passed").sum()
    fail_count = df["RESULT"].str.count("failed").sum()
    
    logging.info("\n==================================")
    logging.info(f"NO. OF PASSED CELL : {pass_count}")
    logging.info(f"NO. OF FAILED CELL : {fail_count}")
    logging.info("==================================\n")


    
    time.sleep(10)
     
    # Move split files into run dir 
    os.system (f"mv -f sc_testcases/sc_report.csv  sc_testcases/sc_split/  {out_dir}")
