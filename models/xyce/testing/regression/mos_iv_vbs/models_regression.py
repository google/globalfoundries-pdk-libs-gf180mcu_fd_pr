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

def ext_measured(device,vgs,vbs):
    
    # Get dimensions used for each device 
    dimensions = pd.read_csv(f"{device}/{device}.csv",usecols=["W (um)" , "L (um)"])
    loops = dimensions["L (um)"].count()
    
    # Extracting measured values for each W & L 
    for i in range (0,loops*2,2):
        width  = dimensions["W (um)"].iloc[int(i/2)]
        length = dimensions["L (um)"].iloc[int(i/2)]
        
        # Special case for 1st measured values 
        if i == 0 :
            # measured Id
            if device in ["pfet_03v3_iv" , "pfet_06v0_iv"]:
                col_list = ['-vgs ',f"vbs ={vbs[0]}",f"vbs ={vbs[1]}",f"vbs ={vbs[2]}",f"vbs ={vbs[3]}",f"vbs ={vbs[4]}"]
            else:
                col_list = ['vgs ',f"vbs ={vbs[0]}",f"vbs ={vbs[1]}",f"vbs ={vbs[2]}",f"vbs ={vbs[3]}",f"vbs ={vbs[4]}"]                
            df_measured = pd.read_csv(f"{device}/{device}.csv",usecols=col_list)
            df_measured.columns = [f"{vgs}",f"vbs ={vbs[0]}",f"vbs ={vbs[1]}",f"vbs ={vbs[2]}",f"vbs ={vbs[3]}",f"vbs ={vbs[4]}"]
            df_measured.to_csv(f"{device}/measured_Id/{int(i/2)}_measured_W{width}_L{length}.csv", index = False)
        else:
            # measured Id
            col_list = [f"{vgs}",f"vbs ={vbs[0]}.{i}",f"vbs ={vbs[1]}.{i}",f"vbs ={vbs[2]}.{i}",f"vbs ={vbs[3]}.{i}",f"vbs ={vbs[4]}.{i}"]
            df_measured = pd.read_csv(f"{device}/{device}.csv",usecols=col_list)
            df_measured.columns = [f"{vgs}",f"vbs ={vbs[0]}",f"vbs ={vbs[1]}",f"vbs ={vbs[2]}",f"vbs ={vbs[3]}",f"vbs ={vbs[4]}"]        
            df_measured.to_csv(f"{device}/measured_Id/{int(i/2)}_measured_W{width}_L{length}.csv", index = False)


def ext_simulated(device,vgs,vbs,vbs_sweep,sim_val):
    
    # Get dimensions used for each device 
    dimensions = pd.read_csv(f"{device}/{device}.csv",usecols=["W (um)" , "L (um)"])
    loops = dimensions["L (um)"].count()
    temp_range = int(loops/3) 
    netlist_tmp = f"./device_netlists_{sim_val}/{device}.spice"
    for i in range (0,loops):
        width  = dimensions["W (um)"].iloc[int(i)]
        length = dimensions["L (um)"].iloc[int(i)]
        AD = float(width) * 0.24
        PD = 2 * (float(width) + 0.24)
        AS = AD 
        PS = PD 
        if i in range (0,temp_range): temp = 25 
        elif i in range (temp_range,2*temp_range): temp = -40 
        else:
            temp = 125 
        with open(netlist_tmp) as f:
            tmpl = Template(f.read())
            os.makedirs(f"{device}/{device}_netlists_{sim_val}",exist_ok=True)
            with open(f"{device}/{device}_netlists_{sim_val}/{i}_{device}_netlist_W{width}_L{length}.spice", "w") as netlist:
                netlist.write(tmpl.render(width = width,length = length,i = i , temp = temp , AD = AD , PD = PD , AS = AS , PS = PD ))
            netlist_path  = f"{device}/{device}_netlists_{sim_val}/{i}_{device}_netlist_W{width}_L{length}.spice" 
            # Running ngspice for each netlist 
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers_count) as executor:
                executor.submit(call_simulator, netlist_path)
            
            # Writing simulated data 
            df_simulated = pd.read_csv(f"{device}/simulated_{sim_val}/{i}_simulated_W{width}_L{length}.csv",header=None, delimiter=r"\s+")
            df_simulated.to_csv(f"{device}/simulated_{sim_val}/{i}_simulated_W{width}_L{length}.csv",index= False)    
            
            # empty array to append in it shaped (vbs_sweep, number of trials + 1)
            new_array = np.empty((vbs_sweep, 1+int(df_simulated.shape[0]/vbs_sweep)))  
            new_array[:, 0] = df_simulated.iloc[:vbs_sweep, 0]
            times = int(df_simulated.shape[0]/vbs_sweep)

            for j in range(times):
                new_array[:, (j+1)] = df_simulated.iloc[j*vbs_sweep:(j+1)*vbs_sweep, 1]
                
            # Writing final simulated data                 
            df_simulated = pd.DataFrame(new_array)
            df_simulated.to_csv(f"{device}/simulated_{sim_val}/{i}_simulated_W{width}_L{length}.csv",index= False)    
            df_simulated.columns = [f"{vgs}",f"vbs ={vbs[0]}",f"vbs ={vbs[1]}",f"vbs ={vbs[2]}",f"vbs ={vbs[3]}",f"vbs ={vbs[4]}"]
            df_simulated.to_csv(f"{device}/simulated_{sim_val}/{i}_simulated_W{width}_L{length}.csv",index= False)    

def error_cal(device,vgs,vbs,sim_val):
    
    # Get dimensions used for each device 
    dimensions = pd.read_csv(f"{device}/{device}.csv",usecols=["W (um)" , "L (um)"])
    loops = dimensions["L (um)"].count()
    temp_range = int(loops/3)     
    df_final = pd.DataFrame()
    for i in range (0,loops):  
        width  = dimensions["W (um)"].iloc[int(i)]
        length = dimensions["L (um)"].iloc[int(i)]
        if i in range (0,temp_range): temp = 25             
        elif i in range (temp_range,2*temp_range): temp = -40             
        else: temp = 125
             
        measured  = pd.read_csv(f"{device}/measured_{sim_val}/{i}_measured_W{width}_L{length}.csv")
        simulated = pd.read_csv(f"{device}/simulated_{sim_val}/{i}_simulated_W{width}_L{length}.csv")

        error_1 = round (100 * abs((abs(measured.iloc[:, 1]) - abs(simulated.iloc[:, 1]))/abs(measured.iloc[:, 1])),6)  
        error_2 = round (100 * abs((abs(measured.iloc[:, 2]) - abs(simulated.iloc[:, 2]))/abs(measured.iloc[:, 2])),6)
        error_3 = round (100 * abs((abs(measured.iloc[:, 3]) - abs(simulated.iloc[:, 3]))/abs(measured.iloc[:, 3])),6) 
        error_4 = round (100 * abs((abs(measured.iloc[:, 4]) - abs(simulated.iloc[:, 4]))/abs(measured.iloc[:, 4])),6) 
        error_5 = round (100 * abs((abs(measured.iloc[:, 5]) - abs(simulated.iloc[:, 5]))/abs(measured.iloc[:, 5])),6) 

        df_error = pd.DataFrame(data=[measured.iloc[:, 0],error_1,error_2,error_3,error_4,error_5]).transpose()        
        df_error.to_csv(f"{device}/error_{sim_val}/{i}_{device}_error_W{width}_L{length}.csv",index= False)
        
        # Mean error 
        mean_error = (df_error[f"vbs ={vbs[0]}"].mean() + df_error[f"vbs ={vbs[1]}"].mean() + df_error[f"vbs ={vbs[2]}"].mean() + 
                      df_error[f"vbs ={vbs[3]}"].mean() + df_error[f"vbs ={vbs[4]}"].mean())/6
        # Max error 
        max_error = df_error[[f"vbs ={vbs[0]}",f"vbs ={vbs[1]}",f"vbs ={vbs[2]}",f"vbs ={vbs[3]}",f"vbs ={vbs[4]}"]].max().max()
        # Max error location 
        max_index = max((df_error == max_error).idxmax())
        max_location_vbs = (df_error == max_error).idxmax(axis=1)[max_index]
        max_location_vgs = df_error[f"{vgs}"][max_index]

        df_final_ = {'Run no.': f'{i}', 'Temp': f'{temp}', 'Device name': f'{device}', 'Width': f'{width}', 'Length': f'{length}', 'Simulated_Val':f'{sim_val}','Mean error%':f'{"{:.2f}".format(mean_error)}', 'Max error%':f'{"{:.2f}".format(max_error)} @ {max_location_vgs} & vbs (V) = {max_location_vbs}'}
        df_final = df_final.append(df_final_, ignore_index = True)
    # Max mean error 
    print (df_final)   
    df_final.to_csv (f"{device}/Final_report_{sim_val}.csv", index = False)
    out_report = pd.read_csv (f"{device}/Final_report_{sim_val}.csv")
    print ("\n",f"Max. mean error = {out_report['Mean error%'].max()}%")    
    print ("=====================================================================================================================================================")

def main():
        
    devices = ["nfet_03v3_iv" , "pfet_03v3_iv" , "nfet_06v0_iv" , "pfet_06v0_iv" , "nfet_06v0_nvt_iv"] #"nfet_03v3_dss_iv"
    nmos_vgs = "vgs (V)"
    pmos_vgs = "-vgs (V)"
    nmos_rds = "Rds"
    Id_sim  = "Id"
    Rds_sim = "Rds"
    mos_3p3_vbs_sweep = 67 
    mos_6p0_vbs_sweep = 121 
    mos_6p0_nat_vbs_sweep = 131     
    nmos3p3_vbs = [0 , -0.825 , -1.65 ,  -2.48 ,  -3.3] 
    pmos3p3_vbs = [0 ,  0.825 ,  1.65 ,   2.48 ,   3.3] 
    nmos6p0_vbs = [ 0 , -0.75 , -1.5 ,  -2.25 ,  -3] 
    pmos6p0_vbs = [ 0 ,  0.75 ,  1.5 ,   2.25 ,   3] 
    nmos6p0_nat_vbs = [ 0 ,  -0.75 , -1.5 , -2.25 , -3]

    for device in devices: 
        # Folder structure of measured values 
        dirpath = f"{device}"
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
        os.makedirs(f"{device}/measured_{Id_sim}",exist_ok=False)
        # os.makedirs(f"{device}/measured_{Rds_sim}",exist_ok=False)

        # From xlsx to csv 
        read_file = pd.read_excel (f"../../180MCU_SPICE_DATA/MOS/{device}.nl_out.xlsx")
        read_file.to_csv (f"{device}/{device}.csv", index = False, header=True)

        # Folder structure of simulated values 
        os.makedirs(f"{device}/simulated_{Id_sim}",exist_ok=False)
        # os.makedirs(f"{device}/simulated_{Rds_sim}",exist_ok=False)
        os.makedirs(f"{device}/error_{Id_sim}",exist_ok=False)
        # os.makedirs(f"{device}/error_{Rds_sim}",exist_ok=False)

    # =========== nfet_03v3_iv ==============      
    ext_measured ("nfet_03v3_iv",nmos_vgs,nmos3p3_vbs)
    ext_simulated("nfet_03v3_iv",nmos_vgs,nmos3p3_vbs,mos_3p3_vbs_sweep,Id_sim)
    error_cal    ("nfet_03v3_iv",nmos_vgs,nmos3p3_vbs,Id_sim)

    # =========== pfet_03v3_iv ==============      
    ext_measured ("pfet_03v3_iv",pmos_vgs,pmos3p3_vbs)
    ext_simulated("pfet_03v3_iv",pmos_vgs,pmos3p3_vbs,mos_3p3_vbs_sweep,Id_sim)
    error_cal    ("pfet_03v3_iv",pmos_vgs,pmos3p3_vbs,Id_sim)

    # =========== nfet_06v0_iv ==============      
    ext_measured ("nfet_06v0_iv",nmos_vgs,nmos6p0_vbs)   
    ext_simulated("nfet_06v0_iv",nmos_vgs,nmos6p0_vbs,mos_6p0_vbs_sweep,Id_sim)
    error_cal    ("nfet_06v0_iv",nmos_vgs,nmos6p0_vbs,Id_sim)    
         
    # =========== pfet_06v0_iv ==============      
    ext_measured ("pfet_06v0_iv",pmos_vgs,pmos6p0_vbs)
    ext_simulated("pfet_06v0_iv",pmos_vgs,pmos6p0_vbs,mos_6p0_vbs_sweep,Id_sim)
    error_cal    ("pfet_06v0_iv",pmos_vgs,pmos6p0_vbs,Id_sim) 
          
    # ============ nfet_03v3_dss_iv =============                                # Error in ngspice 
    # ext_measured ("nfet_03v3_dss_iv",nmos_vgs,nmos3p3_vbs)    
    # ext_simulated("nfet_03v3_dss_iv",nmos_vgs,nmos3p3_vbs,mos_3p3_vbs_sweep,Id_sim)
    # error_cal    ("nfet_03v3_dss_iv",nmos_vgs,nmos3p3_vbs,Rds_sim)

    # ============ nfet_06v0_nvt_iv =============              
    ext_measured ("nfet_06v0_nvt_iv",nmos_vgs,nmos6p0_nat_vbs)
    ext_simulated("nfet_06v0_nvt_iv",nmos_vgs,nmos6p0_nat_vbs,mos_6p0_nat_vbs_sweep,Id_sim)
    error_cal    ("nfet_06v0_nvt_iv",nmos_vgs,nmos6p0_nat_vbs,Id_sim)     

# # ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================
        
if __name__ == "__main__":
    
    # Args 
    arguments     = docopt(__doc__, version='comparator: 0.1')
    workers_count = os.cpu_count()*2 if arguments["--num_cores"] == None else int(arguments["--num_cores"])
    
    # Calling main function 
    main()