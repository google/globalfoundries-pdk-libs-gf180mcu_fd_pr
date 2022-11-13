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

def ext_measured(device,sweep_x,sweep_y,sim_val):
    
    # Get dimensions used for each device 
    dimensions = pd.read_csv(f"{device}/{device}.csv",usecols=["W (um)" , "L (um)"])
    loops = int(dimensions["L (um)"].count()/2)
    
    # Extracting measured values for each W & L 
    for i in range (0,loops):
        width  = dimensions["W (um)"].iloc[int(i)]
        length = dimensions["L (um)"].iloc[int(i)]
        # Special case for 1st measured values 
        if i == 0 :
            # measured Cgc
            if sim_val == "Cgc":
                col_list = [sweep_x,sweep_y[0],sweep_y[1],sweep_y[2],sweep_y[3],sweep_y[4]]
                df_measured = pd.read_csv(f"{device}/{device}.csv",usecols=col_list)                
                df_measured.columns = [sweep_x,sweep_y[0],sweep_y[1],sweep_y[2],sweep_y[3],sweep_y[4]]
            else:
            # measured Cgs & Cgd  
                if sim_val == "Cgs":
                    col_list = [sweep_x,sweep_y[0],sweep_y[1],sweep_y[2],sweep_y[3]]   
                else:
                    col_list = [sweep_x,f"{sweep_y[0]}.1",f"{sweep_y[1]}.1",f"{sweep_y[2]}.1",f"{sweep_y[3]}.1"]
                df_measured = pd.read_csv(f"{device}/{device}.csv",usecols=col_list)            
                df_measured.columns = [sweep_x,sweep_y[0],sweep_y[1],sweep_y[2],sweep_y[3]]
            df_measured.to_csv(f"{device}/measured_{sim_val}/{i}_measured_W{width}_L{length}.csv", index = False)
        else:
            # measured Cgc
            if sim_val == "Cgc":    
                col_list = [sweep_x,f"{sweep_y[0]}.{i}",f"{sweep_y[1]}.{i}",f"{sweep_y[2]}.{i}",f"{sweep_y[3]}.{i}",f"{sweep_y[4]}.{i}"]
                df_measured = pd.read_csv(f"{device}/{device}.csv",usecols=col_list)            
                df_measured.columns = [sweep_x,f"{sweep_y[0]}",f"{sweep_y[1]}",f"{sweep_y[2]}",f"{sweep_y[3]}",f"{sweep_y[4]}"]        
            else:
            # measured Cgs & Cgd 
                cgs_index = 2*i
                cgd_index = cgs_index + 1 
                if sim_val == "Cgs":
                    col_list = [sweep_x,f"{sweep_y[0]}.{cgs_index}",f"{sweep_y[1]}.{cgs_index}",f"{sweep_y[2]}.{cgs_index}",f"{sweep_y[3]}.{cgs_index}"]   
                else: 
                    col_list = [sweep_x,f"{sweep_y[0]}.{cgd_index}",f"{sweep_y[1]}.{cgd_index}",f"{sweep_y[2]}.{cgd_index}",f"{sweep_y[3]}.{cgd_index}"]                       
                df_measured = pd.read_csv(f"{device}/{device}.csv",usecols=col_list)                
                df_measured.columns = [sweep_x,f"{sweep_y[0]}",f"{sweep_y[1]}",f"{sweep_y[2]}",f"{sweep_y[3]}"]                                     
                                
            df_measured.to_csv(f"{device}/measured_{sim_val}/{i}_measured_W{width}_L{length}.csv", index = False)

def ext_simulated(device,sweep_x,sweep_y,vds_sweep,sim_val):
    
    # Get dimensions used for each device 
    dimensions = pd.read_csv(f"{device}/{device}.csv",usecols=["W (um)" , "L (um)"])
    loops = int(dimensions["L (um)"].count()/2)

    netlist_tmp = f"./device_netlists_{sim_val}/{device}.spice"
    for i in range (0,loops):
        width  = dimensions["W (um)"].iloc[int(i)]
        length = dimensions["L (um)"].iloc[int(i)]
        if i == 0:
            nf = 20
        else:
            nf = 1
        with open(netlist_tmp) as f:
            tmpl = Template(f.read())
            os.makedirs(f"{device}/{device}_netlists_{sim_val}",exist_ok=True)
            with open(f"{device}/{device}_netlists_{sim_val}/{i}_{device}_netlist_W{width}_L{length}.spice", "w") as netlist:
                netlist.write(tmpl.render(width = width,length = length,i = i, nf = nf ))
            netlist_path  = f"{device}/{device}_netlists_{sim_val}/{i}_{device}_netlist_W{width}_L{length}.spice" 
            # Running ngspice for each netlist 
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers_count) as executor:
                executor.submit(call_simulator, netlist_path)
            
            # Writing simulated data 
            df_simulated = pd.read_csv(f"{device}/simulated_{sim_val}/{i}_simulated_W{width}_L{length}.csv",header=None, delimiter=r"\s+")
            df_simulated.to_csv(f"{device}/simulated_{sim_val}/{i}_simulated_W{width}_L{length}.csv",index= False)    
            
            # empty array to append in it shaped (vds_sweep, number of trials + 1)
            new_array = np.empty((vds_sweep, 1+int(df_simulated.shape[0]/vds_sweep)))  
            new_array[:, 0] = df_simulated.iloc[:vds_sweep, 0]
            times = int(df_simulated.shape[0]/vds_sweep)

            for j in range(times):
                new_array[:, (j+1)] = df_simulated.iloc[j*vds_sweep:(j+1)*vds_sweep, 1]
                
            # Writing final simulated data                 
            df_simulated = pd.DataFrame(new_array)
            df_simulated.to_csv(f"{device}/simulated_{sim_val}/{i}_simulated_W{width}_L{length}.csv",index= False)
            if sim_val == "Cgc":    
                df_simulated.columns = [sweep_x,sweep_y[0],sweep_y[1],sweep_y[2],sweep_y[3],sweep_y[4]]
            else: 
                df_simulated.columns = [sweep_x,sweep_y[0],sweep_y[1],sweep_y[2],sweep_y[3]]
            df_simulated.to_csv(f"{device}/simulated_{sim_val}/{i}_simulated_W{width}_L{length}.csv",index= False)    
            
def error_cal(device,sweep_x,sweep_y,sim_val):
    
    # Get dimensions used for each device 
    dimensions = pd.read_csv(f"{device}/{device}.csv",usecols=["W (um)" , "L (um)"])
    loops = int(dimensions["L (um)"].count()/2)
    df_final = pd.DataFrame()
    for i in range (0,loops):  
        width  = dimensions["W (um)"].iloc[int(i)]
        length = dimensions["L (um)"].iloc[int(i)]
            
        measured  = pd.read_csv(f"{device}/measured_{sim_val}/{i}_measured_W{width}_L{length}.csv")
        simulated = pd.read_csv(f"{device}/simulated_{sim_val}/{i}_simulated_W{width}_L{length}.csv")

        error_1 = round (100 * (abs(measured.iloc[:, 1]) - abs(simulated.iloc[:, 1]))/abs(measured.iloc[:, 1]),6)  
        error_2 = round (100 * (abs(measured.iloc[:, 2]) - abs(simulated.iloc[:, 2]))/abs(measured.iloc[:, 2]),6)
        error_3 = round (100 * (abs(measured.iloc[:, 3]) - abs(simulated.iloc[:, 3]))/abs(measured.iloc[:, 3]),6) 
        error_4 = round (100 * (abs(measured.iloc[:, 4]) - abs(simulated.iloc[:, 4]))/abs(measured.iloc[:, 4]),6)         
        if sim_val == "Cgc":
            error_5 = round (100 * (abs(measured.iloc[:, 5]) - abs(simulated.iloc[:, 5]))/abs(measured.iloc[:, 5]),6) 
            df_error = pd.DataFrame(data=[measured.iloc[:, 0],error_1,error_2,error_3,error_4,error_5]).transpose()        
        else: 
            df_error = pd.DataFrame(data=[measured.iloc[:, 0],error_1,error_2,error_3,error_4]).transpose()        
        df_error.to_csv(f"{device}/error_{sim_val}/{i}_{device}_error_W{width}_L{length}.csv",index= False)

        # Mean error 
        if sim_val == "Cgc":
            mean_error = (df_error[sweep_y[0]].mean() + df_error[sweep_y[1]].mean() + df_error[sweep_y[2]].mean() + 
                          df_error[sweep_y[3]].mean() + df_error[sweep_y[4]].mean())/5
        else: 
            mean_error = (df_error[sweep_y[0]].mean() + df_error[sweep_y[1]].mean() + df_error[sweep_y[2]].mean() + 
                          df_error[sweep_y[3]].mean())/4 
        # Max error 
        if sim_val == "Cgc":
            max_error = df_error[[sweep_y[0],sweep_y[1],sweep_y[2],sweep_y[3],sweep_y[4]]].max().max()
        else:
            max_error = df_error[[sweep_y[0],sweep_y[1],sweep_y[2],sweep_y[3]]].max().max()
        # Max error location 
        max_index = max((df_error == max_error).idxmax())
        max_location_sweep_y = (df_error == max_error).idxmax(axis=1)[max_index]
        max_location_sweep_x = df_error[sweep_x][max_index]

        df_final_ = {'Run no.': f'{i}', 'Temp': f'25', 'Device name': f'{device}', 'Width': f'{width}', 'Length': f'{length}', 'Simulated_Val':f'{sim_val}','Mean error%':f'{"{:.2f}".format(mean_error)}', 'Max error%':f'{"{:.2f}".format(max_error)} @ {max_location_sweep_y} & {sweep_x}= {max_location_sweep_x}'}
        df_final = df_final.append(df_final_, ignore_index = True)
    # Max mean error 
    print (df_final)   
    df_final.to_csv (f"{device}/Final_report_{sim_val}.csv", index = False)
    out_report = pd.read_csv (f"{device}/Final_report_{sim_val}.csv")
    print ("\n",f"Max. mean error = {out_report['Mean error%'].max()}%")    
    print ("=====================================================================================================================================================")

def main():

    # pandas setup 
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option("max_colwidth", None)
    pd.set_option('display.width', 1000)        
    
    devices = ["nfet_03v3_cv" , "pfet_03v3_cv" ]
    measured_data = ["3p3_cv"]
    nmos_vds = "Vds (V)"
    pmos_vds = "-Vds (V)"
    nmos_vgs = "Vgs (V)"
    pmos_vgs = "-Vgs (V)"
    nmos_rds = "Rds"
    cgc_sim  = "Cgc"
    cgs_sim  = "Cgs"
    cgd_sim  = "Cgd"
    Rds_sim = "Rds"
    mos_3p3_vbs_sweep = 67 
    mos_3p3_vgs_sweep = 34 

    mos_6p0_vgs_sweep = 133 
  
    nmos3p3_vgs = ["Vgs=0"   , "Vgs=1.1"  , "Vgs=2.2"  , "Vgs=3.3" ] 
    pmos3p3_vgs = ["Vgs=-0"  , "Vgs=-1.1" , "Vgs=-2.2" , "Vgs=-3.3"] 
    # pmos3p3_vgs = [-0.8 , -1.3 , -1.8 , -2.3 , -2.8 , -3.3] 
    # nmos6p0_vgs = [ 1 ,  2 ,  3 ,  4 ,  5 ,  6] 
    # pmos6p0_vgs = [-1 , -2 , -3 , -4 , -5 , -6] 
    # nmos6p0_nat_vgs = [ 0.25 ,  1.4 , 2.55 , 3.7 , 4.85 , 6]

    nmos3p3_vbs = ["Vbs=0"  , "Vbs=-0.825" , "Vbs=-1.65" , "Vbs=-2.475" , "Vbs=-3.3"] 
    pmos3p3_vbs = ["Vbs=-0" , "Vbs=0.825"  , "Vbs=1.65"  , "Vbs=2.475"  , "Vbs=3.3" ] 
    # nmos6p0_vbs = [ 0 , -0.75 , -1.5 ,  -2.25 ,  -3] 
    # pmos6p0_vbs = [ 0 ,  0.75 ,  1.5 ,   2.25 ,   3] 
    # nmos6p0_nat_vbs = [ 0 ,  -0.75 , -1.5 , -2.25 , -3]

    for device in devices: 
        # Folder structure of measured values 
        dirpath = f"{device}"
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
        os.makedirs(f"{device}/measured_{cgc_sim}",exist_ok=False)
        os.makedirs(f"{device}/measured_{cgs_sim}",exist_ok=False)
        os.makedirs(f"{device}/measured_{cgd_sim}",exist_ok=False)
        
        # From xlsx to csv 
        read_file = pd.read_excel (f"./measured_data/{measured_data[0]}.nl_out.xlsx")
        read_file.to_csv (f"{device}/{device}.csv", index = False, header=True)

        # Folder structure of simulated values 
        os.makedirs(f"{device}/simulated_{cgc_sim}",exist_ok=False)
        os.makedirs(f"{device}/simulated_{cgs_sim}",exist_ok=False)
        os.makedirs(f"{device}/simulated_{cgd_sim}",exist_ok=False)
        os.makedirs(f"{device}/error_{cgc_sim}",exist_ok=False)
        os.makedirs(f"{device}/error_{cgs_sim}",exist_ok=False)
        os.makedirs(f"{device}/error_{cgd_sim}",exist_ok=False)


    # =========== nfet_03v3_cv ==============      
    # Cgc 
    ext_measured ("nfet_03v3_cv",nmos_vgs,nmos3p3_vbs,cgc_sim)
    ext_simulated("nfet_03v3_cv",nmos_vgs,nmos3p3_vbs,mos_3p3_vbs_sweep,cgc_sim)
    error_cal    ("nfet_03v3_cv",nmos_vgs,nmos3p3_vbs,cgc_sim)

    # Cgs
    ext_measured ("nfet_03v3_cv",nmos_vds,nmos3p3_vgs,cgs_sim)
    ext_simulated("nfet_03v3_cv",nmos_vds,nmos3p3_vgs,mos_3p3_vgs_sweep,cgs_sim)
    error_cal    ("nfet_03v3_cv",nmos_vds,nmos3p3_vgs,cgs_sim)

    # Cgd
    ext_measured ("nfet_03v3_cv",nmos_vds,nmos3p3_vgs,cgd_sim)
    ext_simulated("nfet_03v3_cv",nmos_vds,nmos3p3_vgs,mos_3p3_vgs_sweep,cgd_sim)
    error_cal    ("nfet_03v3_cv",nmos_vds,nmos3p3_vgs,cgd_sim)
    
    
    # =========== nfet_03v3_cv ==============      
    # Cgc
    ext_measured ("pfet_03v3_cv",pmos_vgs,pmos3p3_vbs,cgc_sim)
    ext_simulated("pfet_03v3_cv",pmos_vgs,pmos3p3_vbs,mos_3p3_vbs_sweep,cgc_sim)
    error_cal    ("pfet_03v3_cv",pmos_vgs,pmos3p3_vbs,cgc_sim)
    
    # Cgs
    ext_measured ("pfet_03v3_cv",pmos_vgs,pmos3p3_vgs,cgs_sim)
    ext_simulated("pfet_03v3_cv",pmos_vgs,pmos3p3_vgs,mos_3p3_vgs_sweep,cgs_sim)
    error_cal    ("pfet_03v3_cv",pmos_vgs,pmos3p3_vgs,cgs_sim)
     
    # Cgd   
    ext_measured ("pfet_03v3_cv",pmos_vgs,pmos3p3_vgs,cgd_sim)
    ext_simulated("pfet_03v3_cv",pmos_vgs,pmos3p3_vgs,mos_3p3_vgs_sweep,cgd_sim)
    error_cal    ("pfet_03v3_cv",pmos_vgs,pmos3p3_vgs,cgd_sim)
            
    # =========== pfet_03v3_iv ==============      


    # =========== nfet_06v0_iv ==============      

         
    # =========== pfet_06v0_iv ==============      
      
          
    # ============ nfet_03v3_dss_iv =============                                # Error in ngspice 


    # ============ nfet_06v0_nvt_iv =============              
 
 
# # ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================
        
if __name__ == "__main__":
    
    # Args 
    arguments     = docopt(__doc__, version='comparator: 0.1')
    workers_count = os.cpu_count()*2 if arguments["--num_cores"] == None else int(arguments["--num_cores"])
    
    # Calling main function 
    main()
