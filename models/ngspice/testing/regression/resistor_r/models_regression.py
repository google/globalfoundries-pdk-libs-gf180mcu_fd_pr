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
  models_regression.py [--num_cores=<num>]

  -h, --help             Show help text.
  -v, --version          Show version.
  --num_cores=<num>      Number of cores to be used by simulator
"""

from re import T
from docopt import docopt
import pandas as pd 
import numpy as np
import os 
from jinja2 import Template
import concurrent.futures
import shutil
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def call_simulator(file_name):
    """Call simulation commands to perform simulation.
    Args:
        file_name (str): Netlist file name.
    """
    os.system(f"ngspice -b -a {file_name} -o {file_name}.log > {file_name}.log")

def ext_measured_a(device,vn,d_in, r_sim, corner):
    
    # Get dimensions used for each device 
    dirpath = f"{device}_{r_sim}_{corner}"
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv",usecols=["w (um)" , "l (um)"])
    loops = dimensions["l (um)"].count()
    
    # Extracting measured values for each W & L 
    for i in range (0,loops):
        width  = dimensions["w (um)"].iloc[i]
        length = dimensions["l (um)"].iloc[i]
                                      
        # measured r   
        col_list = [f"{vn}",f"{d_in}_{corner} Rev9 "]
        df_measured = pd.read_csv(f"{dirpath}/{device}.csv",usecols=col_list)
        df_measured.columns = [f"{vn}","value"]
        df_measured.loc[i:i].to_csv(f"{dirpath}/measured_{r_sim}/{i}_measured_w{width}_l{length}.csv", index=False)

def ext_measured_b(device,vn,d_in, r_sim, corner):
    
    # Get dimensions used for each device 
    dirpath = f"{device}_{r_sim}_{corner}_temp"
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv",usecols=["Temperature (C)" , "l (um)"])
    if "rm" in device or "tm" in device:        
        loops = dimensions["l (um)"].count()
    else:
        loops = 11
    
    # Extracting measured values for each W & L 
    for i in range (0,loops):
        temp   = dimensions["Temperature (C)"].iloc[i]
        length = dimensions["l (um)"].iloc[i]
        if "rm" in device or "tm" in device or "_u" in device:        
            width  = length
        else:
            width  = length/2
                                                  
        # measured r   
        col_list = [f"{vn}",f"{d_in}_{corner} Rev9 "]
        df_measured = pd.read_csv(f"{dirpath}/{device}.csv",usecols=col_list)
        df_measured.columns = [f"{vn}","value"]
        df_measured.loc[i:i].to_csv(f"{dirpath}/measured_{r_sim}/{i}_measured_w{width}_l{length}.csv", index=False)

def ext_simulated_a(device,vn,d_in,r_sim, corner,sign):
    
    if "rm" in device or "tm" in device:
        netlist_tmp = f"./device_netlists/2term_res_a.spice"
    else:
        netlist_tmp = f"./device_netlists/3term_res_a.spice"        

    # Get dimensions used for each device 
    dirpath = f"{device}_{r_sim}_{corner}"
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv",usecols=["w (um)" , "l (um)"])
    loops = dimensions["l (um)"].count()
    temp = 25 
    # Extracting measured values for each W & L 
    for i in range (0,loops):
        width  = dimensions["w (um)"].iloc[i]
        length = dimensions["l (um)"].iloc[i]
      
        with open(netlist_tmp) as f:
            tmpl = Template(f.read())
            os.makedirs(f"{dirpath}/{device}_netlists_{r_sim}",exist_ok=True)
            with open(f"{dirpath}/{device}_netlists_{r_sim}/{i}_{device}_netlist_w{width}_l{length}.spice", "w") as netlist:
                netlist.write(tmpl.render(device = device, width = width, length = length , corner = corner, i = i , sign = sign))
            netlist_path  = f"{dirpath}/{device}_netlists_{r_sim}/{i}_{device}_netlist_w{width}_l{length}.spice" 
            # Running ngspice for each netlist 
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers_count) as executor:
                executor.submit(call_simulator, netlist_path)
            
            # Writing simulated data 
            df_simulated = pd.read_csv(f"{dirpath}/simulated_r/{i}_simulated_w{width}_l{length}.csv",header=None, delimiter=r"\s+")
            df_simulated.to_csv(f"{dirpath}/simulated_r/{i}_simulated_w{width}_l{length}.csv",index= False)    

            # Writing final simulated data                 
            df_simulated.columns = [f"{vn}","value"]
            df_simulated.to_csv(f"{dirpath}/simulated_r/{i}_simulated_w{width}_l{length}.csv",index= False) 

def ext_simulated_b(device,vn,d_in,r_sim, corner,sign):
    
    if "rm" in device or "tm" in device:
        netlist_tmp = f"./device_netlists/2term_res_b.spice"
    else:
        netlist_tmp = f"./device_netlists/3term_res_b.spice"        

    # Get dimensions used for each device 
    dirpath = f"{device}_{r_sim}_{corner}_temp"
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv",usecols=["Temperature (C)" , "l (um)"])
    if "rm" in device or "tm" in device:        
        loops = dimensions["l (um)"].count()
    else:
        loops = 11
            
    # Extracting measured values for each W & L 
    for i in range (0,loops):
        temp   = dimensions["Temperature (C)"].iloc[i]
        length = dimensions["l (um)"].iloc[i]
        if "rm" in device or "tm" in device or "_u" in device:        
            width  = length
        else:
            width  = length/2            
        
        with open(netlist_tmp) as f:
            tmpl = Template(f.read())
            os.makedirs(f"{dirpath}/{device}_netlists_{r_sim}",exist_ok=True)
            with open(f"{dirpath}/{device}_netlists_{r_sim}/{i}_{device}_netlist_w{width}_l{length}.spice", "w") as netlist:
                netlist.write(tmpl.render(device = device, temp = temp , width = width, length = length , corner = corner, i = i , sign = sign))
            netlist_path  = f"{dirpath}/{device}_netlists_{r_sim}/{i}_{device}_netlist_w{width}_l{length}.spice" 
            # Running ngspice for each netlist 
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers_count) as executor:
                executor.submit(call_simulator, netlist_path)
            
            # Writing simulated data 
            df_simulated = pd.read_csv(f"{dirpath}/simulated_r/{i}_simulated_w{width}_l{length}.csv",header=None, delimiter=r"\s+")
            df_simulated.to_csv(f"{dirpath}/simulated_r/{i}_simulated_w{width}_l{length}.csv",index= False)    

            # Writing final simulated data                 
            df_simulated.columns = [f"{vn}","value"]
            df_simulated.to_csv(f"{dirpath}/simulated_r/{i}_simulated_w{width}_l{length}.csv",index= False) 
                  
def error_cal_a(device,vn,d_in,r_sim, corner):
    
    df_final = pd.DataFrame()
    # Get dimensions used for each device 
    dirpath = f"{device}_{r_sim}_{corner}"
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv",usecols=["w (um)" , "l (um)"])
    loops = dimensions["l (um)"].count()
    temp = 25 
    # Extracting measured values for each W & L 
    for i in range (0,loops):
        width  = dimensions["w (um)"].iloc[i]
        length = dimensions["l (um)"].iloc[i]
             
        measured  = pd.read_csv(f"{dirpath}/measured_{r_sim}/{i}_measured_w{width}_l{length}.csv")
        simulated = pd.read_csv(f"{dirpath}/simulated_{r_sim}/{i}_simulated_w{width}_l{length}.csv")

        error_1 = round (100 * abs((abs(measured.iloc[:, 1]) - abs(simulated.iloc[:, 1]))/abs(measured.iloc[:, 1])),8)  

        df_error = pd.DataFrame(data=[measured.iloc[:, 0],error_1]).transpose()        
        df_error.to_csv(f"{dirpath}/error_{r_sim}/{i}_{device}_error_w{width}_l{length}.csv",index= False)
        
        # Mean error 
        mean_error = (df_error[f"value"].mean())
        # Max error 
        max_error = df_error[f"value"].max()

        df_final_ = {'Run no.': f'{i}', 'Device name': f'{dirpath}', 'Temperature': temp, 'Width': f'{width}', 'Length': f'{length}', 'Simulated_Val':f'{r_sim}','Mean error%':f'{"{:.2f}".format(mean_error)}', 'Max error%':f'{"{:.2f}".format(max_error)} '}
        df_final = df_final.append(df_final_, ignore_index = True)
    # Max mean error 
    print (df_final)   
    df_final.to_csv (f"{dirpath}/Final_report_{r_sim}.csv", index = False)
    out_report = pd.read_csv (f"{dirpath}/Final_report_{r_sim}.csv")
    print ("\n",f"Max. mean error = {out_report['Mean error%'].max()}%")    
    print ("=====================================================================================================================================================")

def error_cal_b(device,vn,d_in,r_sim, corner):
    
    df_final = pd.DataFrame()
    # Get dimensions used for each device 
    dirpath = f"{device}_{r_sim}_{corner}_temp"
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv",usecols=["Temperature (C)" , "l (um)"])
    if "rm" in device or "tm" in device:        
        loops = dimensions["l (um)"].count()
    else:
        loops = 11
        
    # Extracting measured values for each W & L 
    for i in range (0,loops):
        temp   = dimensions["Temperature (C)"].iloc[i]
        length = dimensions["l (um)"].iloc[i]
        if "rm" in device or "tm" in device or "_u" in device:        
            width  = length
        else:
            width  = length/2   
                         
        measured  = pd.read_csv(f"{dirpath}/measured_{r_sim}/{i}_measured_w{width}_l{length}.csv")
        simulated = pd.read_csv(f"{dirpath}/simulated_{r_sim}/{i}_simulated_w{width}_l{length}.csv")

        error_1 = round (100 * abs((abs(measured.iloc[:, 1]) - abs(simulated.iloc[:, 1]))/abs(measured.iloc[:, 1])),8)  

        df_error = pd.DataFrame(data=[measured.iloc[:, 0],error_1]).transpose()        
        df_error.to_csv(f"{dirpath}/error_{r_sim}/{i}_{device}_error_w{width}_l{length}.csv",index= False)
        
        # Mean error 
        mean_error = (df_error[f"value"].mean())
        # Max error 
        max_error = df_error[f"value"].max()

        df_final_ = {'Run no.': f'{i}', 'Device name': f'{dirpath}', 'Temperature': temp, 'Width': f'{width}', 'Length': f'{length}', 'Simulated_Val':f'{r_sim}','Mean error%':f'{"{:.2f}".format(mean_error)}', 'Max error%':f'{"{:.2f}".format(max_error)} '}
        df_final = df_final.append(df_final_, ignore_index = True)
    # Max mean error 
    print (df_final)   
    df_final.to_csv (f"{dirpath}/Final_report_{r_sim}.csv", index = False)
    out_report = pd.read_csv (f"{dirpath}/Final_report_{r_sim}.csv")
    print ("\n",f"Max. mean error = {out_report['Mean error%'].max()}%")    
    print ("=====================================================================================================================================================")

def main():

    # res W&L var. 
    corners_a  = ["typical","ff","ss"]        
    
    devices_a  = ["nplus_u" , "pplus_u" , "nplus_s" , "pplus_s" , "npolyf_u" , "ppolyf_u" , "npolyf_s" , "ppolyf_s" , "ppolyf_u_1k" , "ppolyf_u_2k" , "ppolyf_u_1k_6p0" ,
                  "ppolyf_u_2k_6p0" , "ppolyf_u_3k" , "rm1" , "rm2" , "rm3" , "tm6k" , "tm9k" , "tm11k" , "tm30k" , "nwell"]
    
    dev_data_a = ["RES01a-wl-nplus_u.nl_out"     ,"RES02a-wl-pplus_u.nl_out"       ,"RES03a-wl-nplus_s.nl_out"       , "RES04a-wl-pplus_s.nl_out"     , 
                  "RES06a-wl-npolyf_u.nl_out"    ,"RES07a-wl-ppolyf_u.nl_out"      ,"RES08a-wl-npolyf_s.nl_out"      , "RES09a-wl-ppolyf_s.nl_out"    , "RES10a-wl-ppolyf_u_1k.nl_out", 
                  "RES11a-wl-ppolyf_u_2k.nl_out" ,"RES12a-wl-ppolyf_u_1k_6p0.nl_o" ,"RES13a-wl-ppolyf_u_2k_6p0.nl_o" , "RES14a-wl-ppolyf_u_3k.nl_out" , 
                  "RES15a-wl-rm1.nl_out"         , "RES16a-wl-rm2.nl_out"          , "RES17a-wl-rm3.nl_out"          , "RES18a-wl-tm6k.nl_out"        , "RES19a-wl-tm9k.nl_out" ,
                  "RES20a-wl-tm11k.nl_out"       , "RES21a-wl-tm30k.nl_out" ,"RES05a-wl-nwell.nl_out"]
    
    sign_a     = ["+" , "-" , "+" , "-" , "+" , "+" , "-" , "+" , "-" , "-" , "-" , "-" , "-" , "-" , "+" , "+" , "+" , "+" , "+" , "+", "+", ""]
    measure_a  = ["r","corners", "res"]
   
    for corner in corners_a: 
        for i,device in enumerate(devices_a): 
            # Folder structure of measured values
            r_sim, res_vn, res_in = measure_a[0], measure_a[1], measure_a[2]
            dirpath = f"{device}_{r_sim}_{corner}"
            if os.path.exists(dirpath) and os.path.isdir(dirpath):
                shutil.rmtree(dirpath)
            os.makedirs(f"{dirpath}/measured_{r_sim}",exist_ok=False)

            # From xlsx to csv
            read_file = pd.read_excel (f"../../180MCU_SPICE_DATA/Resistor/{dev_data_a[i]}.xlsx")
            read_file.to_csv (f"{dirpath}/{device}.csv", index = False, header=True)

            # Folder structure of simulated values 
            os.makedirs(f"{dirpath}/simulated_{r_sim}",exist_ok=False)
            os.makedirs(f"{dirpath}/error_{r_sim}",exist_ok=False)
    
            ext_measured_a (device,res_vn,res_in, r_sim, corner)
            ext_simulated_a(device,res_vn,res_in,r_sim, corner,sign_a[i])
            error_cal_a    (device,res_vn,res_in,r_sim, corner)            


    # res temp_var
    corners_b  = ["typical","ff","ss"]        
    devices_b  = ["nplus_u" , "nplus_s", "pplus_u" , "pplus_s" , "nwell" , "npolyf_u" , "ppolyf_u" , "npolyf_s" , "ppolyf_s" , "ppolyf_u_1k" , "ppolyf_u_2k" , "ppolyf_u_1k_6p0" , "ppolyf_u_2k_6p0" , "ppolyf_u_3k" ,
                  "rm1" , "rm2", "rm3" , "tm6k" , "tm9k" , "tm11k", "tm30k"]
    dev_data_b = ["RES01b-temp-nplus_u.nl_out" , "RES03b-temp-nplus_s.nl_out", "RES02b-temp-pplus_u.nl_out" , "RES04b-temp-pplus_s.nl_out" , "RES05b-temp-nwell.nl_out" ,
                  "RES06b-temp-npolyf_u.nl_out" , "RES07b-temp-ppolyf_u.nl_out" ,  "RES08b-temp-npolyf_s.nl_out" , "RES09b-temp-ppolyf_s.nl_out" , "RES10b-temp-ppolyf_u_1k.nl_out" ,
                  "RES11b-temp-ppolyf_u_2k.nl_out" , "RES12b-temp-ppolyf_u_1k_6p0.nl" , "RES13b-temp-ppolyf_u_2k_6p0.nl" , "RES14b-temp-ppolyf_u_3k.nl_out" ,   
                  "RES15b-temp-rm1.nl_out", "RES16b-temp-rm2.nl_out" , "RES17b-temp-rm3.nl_out" ,
                  "RES18b-temp-tm6k.nl_out", "RES19b-temp-tm9k.nl_out" , "RES20b-temp-tm11k.nl_out", "RES21b-temp-tm30k.nl_out"]
    
    sign_b     = ["+" , "+", "-" , "-" , "+" , "+" , "-" ,"+" , "-" , "-" , "-" , "-" , "-" , "-" , "+" , "+" , "+" , "+" , "+" , "+", "+"]
    measure_b  = ["r","corners", "res"]
   
    for corner in corners_b: 
        for i,device in enumerate(devices_b): 
            # Folder structure of measured values
            r_sim, res_vn, res_in = measure_b[0], measure_b[1], measure_b[2]
            dirpath = f"{device}_{r_sim}_{corner}_temp"
            if os.path.exists(dirpath) and os.path.isdir(dirpath):
                shutil.rmtree(dirpath)
            os.makedirs(f"{dirpath}/measured_{r_sim}",exist_ok=False)

            # From xlsx to csv
            read_file = pd.read_excel (f"../../180MCU_SPICE_DATA/Resistor/{dev_data_b[i]}.xlsx")
            read_file.to_csv (f"{dirpath}/{device}.csv", index = False, header=True)

            # Folder structure of simulated values 
            os.makedirs(f"{dirpath}/simulated_{r_sim}",exist_ok=False)
            os.makedirs(f"{dirpath}/error_{r_sim}",exist_ok=False)
    
            ext_measured_b (device,res_vn,res_in, r_sim, corner)
            ext_simulated_b(device,res_vn,res_in,r_sim, corner,sign_b[i])
            error_cal_b    (device,res_vn,res_in,r_sim, corner)  


# # ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================
        
if __name__ == "__main__":
    
    # Args 
    arguments     = docopt(__doc__, version='comparator: 0.1')
    workers_count = os.cpu_count()*2 if arguments["--num_cores"] == None else int(arguments["--num_cores"])
    
    # Calling main function 
    main()
