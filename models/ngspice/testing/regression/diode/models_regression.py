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

def ext_measured(device,vn,d_in, Id_sim, corner):
    
    # Get dimensions used for each device 
    dirpath = f"{device}_{Id_sim}_{corner}"
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv",usecols=["W (um)" , "L (um)"])
    loops = dimensions["L (um)"].count()
    
    # Extracting measured values for each W & L 
    for i in range (0,loops):
        width  = dimensions["W (um)"].iloc[i]
        length = dimensions["L (um)"].iloc[i]
        
        # Special case for 1st measured values 
        if i == 0 :
            # measured Id
            col_list = [f"{vn}",f"{d_in}_{corner}"]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv",usecols=col_list)
            df_measured.columns = [f"{vn}",f"{d_in}_{corner}"]
            df_measured.to_csv(f"{dirpath}/measured_{Id_sim}/{i}_measured_A{width}_P{length}.csv", index = False)
        else:
            # measured Id
            col_list = [f"{vn}",f"{d_in}_{corner}.{i}"]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv",usecols=col_list)
            df_measured.columns = [f"{vn}",f"{d_in}_{corner}"]        
            df_measured.to_csv(f"{dirpath}/measured_{Id_sim}/{i}_measured_A{width}_P{length}.csv", index = False)

def ext_simulated(device,vn,d_in,vn_sweeps,Id_sim, corner):
    
    # Get dimensions used for each device 
    dirpath = f"{device}_{Id_sim}_{corner}"
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv",usecols=["W (um)" , "L (um)"])
    loops = dimensions["L (um)"].count()
    netlist_tmp = f"./device_netlists/{Id_sim}.spice"
    for i in range (0,loops):
        width  = dimensions["W (um)"].iloc[int(i)]
        length = dimensions["L (um)"].iloc[int(i)]

        if i % 4 == 0: temp = -40 
        elif i % 4 == 1: temp = 25 
        elif i % 4 == 2: temp = 125
        else:
            temp = 175 
        with open(netlist_tmp) as f:
            tmpl = Template(f.read())
            os.makedirs(f"{dirpath}/{device}_netlists_{Id_sim}",exist_ok=True)
            with open(f"{dirpath}/{device}_netlists_{Id_sim}/{i}_{device}_netlist_A{width}_P{length}.spice", "w") as netlist:
                netlist.write(tmpl.render(device = device, area = width, pj = length, i = i , temp = temp, Id_sim = Id_sim , corner = corner ))
            netlist_path  = f"{dirpath}/{device}_netlists_{Id_sim}/{i}_{device}_netlist_A{width}_P{length}.spice" 
            # Running ngspice for each netlist 
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers_count) as executor:
                executor.submit(call_simulator, netlist_path)
            
            # Writing simulated data 
            df_simulated = pd.read_csv(f"{dirpath}/simulated_{Id_sim}/{i}_simulated_A{width}_P{length}.csv",header=None, delimiter=r"\s+")
            df_simulated.to_csv(f"{dirpath}/simulated_{Id_sim}/{i}_simulated_A{width}_P{length}.csv",index= False)    
            
            # empty array to append in it shaped (vn_sweeps, number of trials + 1)
            new_array = np.empty((vn_sweeps, 1+int(df_simulated.shape[0]/vn_sweeps)))  
            new_array[:, 0] = df_simulated.iloc[:vn_sweeps, 0]
            times = int(df_simulated.shape[0]/vn_sweeps)

            for j in range(times):
                new_array[:, (j+1)] = df_simulated.iloc[j*vn_sweeps:(j+1)*vn_sweeps, 1]
                
            # Writing final simulated data                 
            df_simulated = pd.DataFrame(new_array)
            df_simulated.to_csv(f"{dirpath}/simulated_{Id_sim}/{i}_simulated_A{width}_P{length}.csv",index= False)    
            df_simulated.columns = [f"{vn}",f"{d_in}_{corner}"]
            df_simulated.to_csv(f"{dirpath}/simulated_{Id_sim}/{i}_simulated_A{width}_P{length}.csv",index= False)    

def error_cal(device,vn,d_in,Id_sim, corner):
    
    # Get dimensions used for each device 
    dirpath = f"{device}_{Id_sim}_{corner}"
    dimensions = pd.read_csv(f"{dirpath}/{device}.csv",usecols=["W (um)" , "L (um)"])
    loops = dimensions["L (um)"].count()    
    df_final = pd.DataFrame()
    for i in range (0,loops):  
        width  = dimensions["W (um)"].iloc[int(i)]
        length = dimensions["L (um)"].iloc[int(i)]
        if i % 4 == 0: temp = -40 
        elif i % 4 == 1: temp = 25 
        elif i % 4 == 2: temp = 125
        else:
            temp = 175 
             
        measured  = pd.read_csv(f"{dirpath}/measured_{Id_sim}/{i}_measured_A{width}_P{length}.csv")
        simulated = pd.read_csv(f"{dirpath}/simulated_{Id_sim}/{i}_simulated_A{width}_P{length}.csv")

        error_1 = round (100 * abs((abs(measured.iloc[:, 1]) - abs(simulated.iloc[:, 1]))/abs(measured.iloc[:, 1])),6)  

        df_error = pd.DataFrame(data=[measured.iloc[:, 0],error_1]).transpose()        
        df_error.to_csv(f"{dirpath}/error_{Id_sim}/{i}_{device}_error_A{width}_P{length}.csv",index= False)
        
        # Mean error 
        mean_error = (df_error[f"{d_in}_{corner}"].mean())/6
        # Max error 
        max_error = df_error[f"{d_in}_{corner}"].max()
        # Max error location 
        max_index = max((df_error == max_error).idxmax())
        max_location_vgs = (df_error == max_error).idxmax(axis=1)[max_index]
        max_location_vds = df_error[f"{vn}"][max_index]

        df_final_ = {'Run no.': f'{i}', 'Temp': f'{temp}', 'Device name': f'{dirpath}', 'Area': f'{width}', 'Perimeter': f'{length}', 'Simulated_Val':f'{Id_sim}','Mean error%':f'{"{:.2f}".format(mean_error)}', 'Max error%':f'{"{:.2f}".format(max_error)} @ {max_location_vgs} & vn (V) = {max_location_vds}'}
        df_final = df_final.append(df_final_, ignore_index = True)
    # Max mean error 
    print (df_final)   
    df_final.to_csv (f"{dirpath}/Final_report_{Id_sim}.csv", index = False)
    out_report = pd.read_csv (f"{dirpath}/Final_report_{Id_sim}.csv")
    print ("\n",f"Max. mean error = {out_report['Mean error%'].max()}%")    
    print ("=====================================================================================================================================================")

def main():
        
    devices = ["diode_dw2ps_06v0","diode_pw2dw_06v0","diode_nd2ps_03v3","diode_nd2ps_06v0", "diode_nw2ps_03v3","diode_nw2ps_06v0","diode_pd2nw_03v3","diode_pd2nw_06v0","sc_diode"]
    corners = ["typical","ff","ss"]
    measures = [["iv","Vn1 (V)", " |In1(A)| diode", 103],
                 ["cv","Vj", "diode", 17]]

    for device in devices: 
        for measure in measures:
            for corner in corners: 
                # Folder structure of measured values
                Id_sim, diode_vn, diode_in, no_of_vn_sweeps = measure[0], measure[1], measure[2], measure[3] 
                dirpath = f"{device}_{Id_sim}_{corner}"
                if os.path.exists(dirpath) and os.path.isdir(dirpath):
                    shutil.rmtree(dirpath)
                os.makedirs(f"{dirpath}/measured_{Id_sim}",exist_ok=False)

                # From xlsx to csv 
                read_file = pd.read_excel (f"./0_measured_data/{device}_{Id_sim}.nl_out.xlsx")
                read_file.to_csv (f"{dirpath}/{device}.csv", index = False, header=True)

                # Folder structure of simulated values 
                os.makedirs(f"{dirpath}/simulated_{Id_sim}",exist_ok=False)
                os.makedirs(f"{dirpath}/error_{Id_sim}",exist_ok=False)
        
                ext_measured (device,diode_vn,diode_in, Id_sim, corner)

                ext_simulated(device,diode_vn,diode_in,no_of_vn_sweeps,Id_sim, corner)
                error_cal    (device,diode_vn,diode_in,Id_sim, corner)


    
# # ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================
        
if __name__ == "__main__":
    
    # Args 
    arguments     = docopt(__doc__, version='comparator: 0.1')
    workers_count = os.cpu_count()*2 if arguments["--num_cores"] == None else int(arguments["--num_cores"])
    
    # Calling main function 
    main()
