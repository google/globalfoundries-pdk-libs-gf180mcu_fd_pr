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
    os.system(f"Xyce -hspice-ext all {file_name} -l {file_name}.log")

def ext_measured(device,vn,d_in, cv_sim, corner,start):
    
    # Get dimensions used for each device 
    dirpath = f"{device}_{cv_sim}_{corner}"
    
    # Extracting measured values for each W & L 
    for i in range (start,4+start):
        if i == 0+start: width  = 50 ; length = 50
        if i == 1+start: width  = 1  ; length = 1
        if i == 2+start: width  = 50 ; length = 1
        if i == 3+start: width  = 1  ; length = 50

        if i == 0 :                       
            # measured cv
            col_list = [f"Vj",f"moscap_{corner}"]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv",usecols=col_list)
            df_measured.to_csv(f"{dirpath}/measured_{cv_sim}/{i-start}_measured_w{width}_l{length}.csv", index=False)
        else:
            # measured cv
            col_list = [f"Vj",f"moscap_{corner}.{i}"]
            df_measured = pd.read_csv(f"{dirpath}/{device}.csv",usecols=col_list)
            df_measured.columns = [f"Vj",f"moscap_{corner}"]
            df_measured.to_csv(f"{dirpath}/measured_{cv_sim}/{i-start}_measured_w{width}_l{length}.csv", index=False)

def ext_simulated(device,vn,d_in,cv_sim, corner,start,voltage):
    
    # Get dimensions used for each device 
    dirpath = f"{device}_{cv_sim}_{corner}"
    netlist_tmp = f"./device_netlists/moscap.spice"
    
    # Extracting measured values for each W & L 
    for i in range (start,4+start):
        if i == 0+start: width  = 50 ; length = 50
        if i == 1+start: width  = 1  ; length = 1
        if i == 2+start: width  = 50 ; length = 1
        if i == 3+start: width  = 1  ; length = 50
    
        with open(netlist_tmp) as f:
            tmpl = Template(f.read())
            os.makedirs(f"{dirpath}/{device}_netlists_{cv_sim}",exist_ok=True)
            with open(f"{dirpath}/{device}_netlists_{cv_sim}/{i-start}_{device}_netlist_w{width}_l{length}.spice", "w") as netlist:
                netlist.write(tmpl.render(device = device, width = width, length = length , corner = corner , voltage = voltage))
            netlist_path  = f"{dirpath}/{device}_netlists_{cv_sim}/{i-start}_{device}_netlist_w{width}_l{length}.spice" 
            # Running ngspice for each netlist 
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers_count) as executor:
                executor.submit(call_simulator, netlist_path)
            
        # Writing simulated data 
        df_simulated = []
        # Writing simulated data 
        for j in range(len([x for x in os.listdir(f"{dirpath}/{device}_netlists_{cv_sim}") if f"{i-start}_{device}_netlist_w{width}_l{length}.spice.ma" in x])):
            with open(f"{dirpath}/{device}_netlists_{cv_sim}/{i-start}_{device}_netlist_w{width}_l{length}.spice.ma{j}") as f:
                cap = 1000000/(float(next(f).replace("FREQ = ", ""))*2*np.pi)
                df_simulated.append(cap) 
        
        # zero array to append in it shaped (vn_sweeps, number of trials + 1)
        new_array = np.zeros((len(df_simulated), 2))
        new_array[:len(df_simulated), 0] = df_simulated
        new_array[:len(df_simulated), 1] = df_simulated

        # Writing final simulated data                 
        df_simulated = pd.DataFrame(new_array)   
        df_simulated.columns = [f"Vj",f"moscap_{corner}"]
        df_simulated.to_csv(f"{dirpath}/simulated_{cv_sim}/{i-start}_simulated_w{width}_l{length}.csv",index= False)     
            
def error_cal(device,vn,d_in,Id_sim, corner,start):
    
    # Get dimensions used for each device 
    dirpath = f"{device}_{Id_sim}_{corner}"
    df_final = pd.DataFrame()
    for i in range (start,4+start):
        if i == 0+start: width  = 50 ; length = 50
        if i == 1+start: width  = 1  ; length = 1
        if i == 2+start: width  = 50 ; length = 1
        if i == 3+start: width  = 1  ; length = 50
             
        measured  = pd.read_csv(f"{dirpath}/measured_{Id_sim}/{i-start}_measured_w{width}_l{length}.csv")
        simulated = pd.read_csv(f"{dirpath}/simulated_{Id_sim}/{i-start}_simulated_w{width}_l{length}.csv")

        error_1 = round (100 * abs((abs(measured.iloc[:, 1]) - abs(simulated.iloc[:, 1]))/abs(measured.iloc[:, 1])),8)  

        df_error = pd.DataFrame(data=[measured.iloc[:, 0],error_1]).transpose()        
        df_error.to_csv(f"{dirpath}/error_{Id_sim}/{i-start}_{device}_error_w{width}_l{length}.csv",index= False)
        
        # Mean error 
        mean_error = (df_error[f"moscap_{corner}"].mean())
        # Max error 
        max_error = df_error[f"moscap_{corner}"].max()

        df_final_ = {'Run no.': f'{i-start}', 'Device name': f'{dirpath}', 'Width': f'{width}', 'Length': f'{length}', 'Simulated_Val':f'{Id_sim}','Mean error%':f'{"{:.2f}".format(mean_error)}', 'Max error%':f'{"{:.2f}".format(max_error)} '}
        df_final = df_final.append(df_final_, ignore_index = True)
    
    # Max mean error 
    print (df_final)   
    df_final.to_csv (f"{dirpath}/Final_report_{Id_sim}.csv", index = False)
    out_report = pd.read_csv (f"{dirpath}/Final_report_{Id_sim}.csv")
    print ("\n",f"Max. mean error = {out_report['Mean error%'].max()}%")    
    print ("=====================================================================================================================================================")


def main():

    # 3p3
    corners = ["typical","ff","ss"]        
    devices = ["cap_nmos_03v3" , "cap_pmos_03v3" , "cap_nmos_03v3_b" , "cap_pmos_03v3_b"]
    measure = ["cv","corners", "CV (fF)"]
    voltage = ["-3.3 3.3 0.1","-6.6 6.0 0.1"]
    start = 0
    for corner in corners: 
        for device in devices: 
            # Folder structure of measured values
            cv_sim, cap_vn, cap_in = measure[0], measure[1], measure[2]
            dirpath = f"{device}_{cv_sim}_{corner}"
            if os.path.exists(dirpath) and os.path.isdir(dirpath):
                shutil.rmtree(dirpath)
            os.makedirs(f"{dirpath}/measured_{cv_sim}",exist_ok=False)

            # From xlsx to csv
            read_file = pd.read_excel (f"../../180MCU_SPICE_DATA/Cap/moscap_cv_3p3.nl_out.xlsx")
            read_file.to_csv (f"{dirpath}/{device}.csv", index = False, header=True)

            # Folder structure of simulated values 
            os.makedirs(f"{dirpath}/simulated_{cv_sim}",exist_ok=False)
            os.makedirs(f"{dirpath}/error_{cv_sim}",exist_ok=False)
    
            ext_measured (device,cap_vn,cap_in, cv_sim, corner,start)
            ext_simulated(device,cap_vn,cap_in,cv_sim, corner,start,voltage[0])
            error_cal    (device,cap_vn,cap_in,cv_sim, corner,start)            
            start = start + 4            
        start = 0

    # 6p0 
    corners = ["typical","ff","ss"]        
    devices = ["cap_nmos_06v0" , "cap_pmos_06v0" , "cap_nmos_06v0_b" , "cap_pmos_06v0_b"]
    measure = ["cv","corners", "CV (fF)"]
    start = 0
    for corner in corners: 
        for device in devices: 
            # Folder structure of measured values
            cv_sim, cap_vn, cap_in = measure[0], measure[1], measure[2]
            dirpath = f"{device}_{cv_sim}_{corner}"
            if os.path.exists(dirpath) and os.path.isdir(dirpath):
                shutil.rmtree(dirpath)
            os.makedirs(f"{dirpath}/measured_{cv_sim}",exist_ok=False)

            # From xlsx to csv
            read_file = pd.read_excel (f"../../180MCU_SPICE_DATA/Cap/moscap_cv_6p0.nl_out.xlsx")
            read_file.to_csv (f"{dirpath}/{device}.csv", index = False, header=True)

            # Folder structure of simulated values 
            os.makedirs(f"{dirpath}/simulated_{cv_sim}",exist_ok=False)
            os.makedirs(f"{dirpath}/error_{cv_sim}",exist_ok=False)
    
            ext_measured (device,cap_vn,cap_in, cv_sim, corner,start)
            ext_simulated(device,cap_vn,cap_in,cv_sim, corner,start,voltage[1])
            error_cal    (device,cap_vn,cap_in,cv_sim, corner,start)            
            start = start + 4            
        start = 0

        # 3p3
    corners = ["typical","ff","ss"]        
    devices = ["cap_nmos_03v3" , "cap_pmos_03v3" , "cap_nmos_03v3_b" , "cap_pmos_03v3_b"]
    measure = ["cv","corners", "CV (fF)"]
    start = 0
    for corner in corners: 
        for device in devices: 
            # Folder structure of measured values
            cv_sim, cap_vn, cap_in = measure[0], measure[1], measure[2]
            error_cal    (device,cap_vn,cap_in,cv_sim, corner,start)            
            start = start + 4            
        start = 0

    # 6p0 
    corners = ["typical","ff","ss"]        
    devices = ["cap_nmos_06v0" , "cap_pmos_06v0" , "cap_nmos_06v0_b" , "cap_pmos_06v0_b"]
    measure = ["cv","corners", "CV (fF)"]
    start = 0
    for corner in corners: 
        for device in devices: 
            # Folder structure of measured values
            cv_sim, cap_vn, cap_in = measure[0], measure[1], measure[2]
            error_cal    (device,cap_vn,cap_in,cv_sim, corner,start)            
            start = start + 4            
        start = 0

# # ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================
        
if __name__ == "__main__":
    
    # Args 
    arguments     = docopt(__doc__, version='comparator: 0.1')
    workers_count = os.cpu_count()*2 if arguments["--num_cores"] == None else int(arguments["--num_cores"])
    
    # Calling main function 
    main()
