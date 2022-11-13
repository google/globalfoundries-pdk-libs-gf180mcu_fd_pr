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

def ext_measured(device,vc,step,Id_sim,list_devices,ib):

    # Get dimensions used for each device 
    dimensions = pd.read_csv(f"{device}/{device}.csv",usecols=["corners"])
    loops = dimensions["corners"].count()

    # Extracting measured values for each Device 
    for i in range (loops):
        k = i
        if i >= len(list_devices):
            while k >= len(list_devices):
                k = k - len(list_devices)

        # Special case for 1st measured values 
        if i == 0 :
            if device == "pnp":
                temp_vc = vc
                vc = "-vc "
            # measured Id_sim
            col_list = [f"{vc}",f"{ib}{step[0]}",f"{ib}{step[1]}",f"{ib}{step[2]}",f"{ib}{step[3]}",f"{ib}{step[4]}"]
            df_measured = pd.read_csv(f"{device}/{device}.csv",usecols=col_list)
            df_measured.columns = [f"{vc}",f"{ib}{step[0]}",f"{ib}{step[1]}",f"{ib}{step[2]}",f"{ib}{step[3]}",f"{ib}{step[4]}"]
            df_measured.to_csv(f"{device}/measured_{Id_sim}/{i}_measured_{list_devices[k]}.csv", index = False)
        else:
            if device == "pnp":
                vc = temp_vc
            # measured Id_sim
            col_list = [f"{vc}",f"{ib}{step[0]}.{i}",f"{ib}{step[1]}.{i}",f"{ib}{step[2]}.{i}",f"{ib}{step[3]}.{i}",f"{ib}{step[4]}.{i}"]
            df_measured = pd.read_csv(f"{device}/{device}.csv",usecols=col_list)
            df_measured.columns = [f"{vc}",f"{ib}{step[0]}",f"{ib}{step[1]}",f"{ib}{step[2]}",f"{ib}{step[3]}",f"{ib}{step[4]}"]        
            df_measured.to_csv(f"{device}/measured_{Id_sim}/{i}_measured_{list_devices[k]}.csv", index = False)

def ext_simulated(device,vc,step,sweep,Id_sim,list_devices,ib):

    # Get dimensions used for each device 
    dimensions = pd.read_csv(f"{device}/{device}.csv",usecols=["corners"])
    loops = dimensions["corners"].count()
    temp_range = int(loops/4) 
    netlist_tmp = f"./device_netlists/{device}.spice"
    for i in range (loops):
        if i in range (0,temp_range):               temp = 25
        elif i in range (temp_range,2*temp_range):  temp = -40
        elif i in range (2*temp_range,3*temp_range):temp = 125
        else:                                       temp = 175 

        k = i
        if i >= len(list_devices):
            while k >= len(list_devices):
                k = k - len(list_devices)

        with open(netlist_tmp) as f:
            tmpl = Template(f.read())
            os.makedirs(f"{device}/{device}_netlists_{Id_sim}",exist_ok=True)
            with open(f"{device}/{device}_netlists_{Id_sim}/{i}_{device}_netlist_{list_devices[k]}.spice", "w") as netlist:
                netlist.write(tmpl.render(device = list_devices[k], i = i , temp = temp ))
            netlist_path  = f"{device}/{device}_netlists_{Id_sim}/{i}_{device}_netlist_{list_devices[k]}.spice" 

            # Running ngspice for each netlist 
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers_count) as executor:
                executor.submit(call_simulator, netlist_path)

            # Writing simulated data 
            df_simulated = pd.read_csv(f"{device}/simulated_{Id_sim}/{i}_simulated_{list_devices[k]}.csv",header=None, delimiter=r"\s+")

            # empty array to append in it shaped (sweep, number of trials + 1)
            new_array = np.empty((sweep, 1+int(df_simulated.shape[0]/sweep)))  
            new_array[:, 0] = df_simulated.iloc[:sweep, 0]
            times = int(df_simulated.shape[0]/sweep)

            for j in range(times):
                new_array[:, (j+1)] = df_simulated.iloc[j*sweep:(j+1)*sweep, 1]

            # Writing final simulated data                 
            df_simulated = pd.DataFrame(new_array)
            df_simulated.to_csv(f"{device}/simulated_{Id_sim}/{i}_simulated_{list_devices[k]}.csv",index= False)    
            df_simulated.columns = [f"{vc}",f"{ib}{step[0]}",f"{ib}{step[1]}",f"{ib}{step[2]}",f"{ib}{step[3]}",f"{ib}{step[4]}"]
            df_simulated.to_csv(f"{device}/simulated_{Id_sim}/{i}_simulated_{list_devices[k]}.csv",index= False)

def error_cal(device,vc,step,Id_sim,list_devices,ib):

    df_final = pd.DataFrame()
    # Get dimensions used for each device 
    dimensions = pd.read_csv(f"{device}/{device}.csv",usecols=["corners"])
    loops = dimensions["corners"].count()
    temp_range = int(loops/4) 
    for i in range (loops):
        if i in range (0,temp_range):               temp = 25
        elif i in range (temp_range,2*temp_range):  temp = -40
        elif i in range (2*temp_range,3*temp_range):temp = 125
        else:                                       temp = 175 

        k = i
        if i >= len(list_devices):
            while k >= len(list_devices):
                k = k - len(list_devices)

        measured  = pd.read_csv(f"{device}/measured_{Id_sim}/{i}_measured_{list_devices[k]}.csv")
        simulated = pd.read_csv(f"{device}/simulated_{Id_sim}/{i}_simulated_{list_devices[k]}.csv")

        error_1 = round (100 * abs((abs(measured.iloc[0:, 1]) - abs(simulated.iloc[0:, 1]))/abs(measured.iloc[:, 1])),6)  
        error_2 = round (100 * abs((abs(measured.iloc[0:, 2]) - abs(simulated.iloc[0:, 2]))/abs(measured.iloc[:, 2])),6)
        error_3 = round (100 * abs((abs(measured.iloc[0:, 3]) - abs(simulated.iloc[0:, 3]))/abs(measured.iloc[:, 3])),6) 
        error_4 = round (100 * abs((abs(measured.iloc[0:, 4]) - abs(simulated.iloc[0:, 4]))/abs(measured.iloc[:, 4])),6) 
        error_5 = round (100 * abs((abs(measured.iloc[0:, 5]) - abs(simulated.iloc[0:, 5]))/abs(measured.iloc[:, 5])),6)

        df_error = pd.DataFrame(data=[measured.iloc[:, 0],error_1,error_2,error_3,error_4,error_5]).transpose()        
        df_error.to_csv(f"{device}/error_{Id_sim}/{i}_{device}_error_{list_devices[k]}.csv",index= False)

        # Mean error 
        mean_error = (df_error[f"{ib}{step[0]}"].mean() + df_error[f"{ib}{step[1]}"].mean() + df_error[f"{ib}{step[2]}"].mean() + 
                      df_error[f"{ib}{step[3]}"].mean() + df_error[f"{ib}{step[4]}"].mean())/6
        # Max error 
        max_error = df_error[[f"{ib}{step[0]}",f"{ib}{step[1]}",f"{ib}{step[2]}",f"{ib}{step[3]}",f"{ib}{step[4]}"]].max().max()
        # Max error location 
        max_index = max((df_error == max_error).idxmax())
        max_location_ib = (df_error == max_error).idxmax(axis=1)[max_index]
        if i == 0 :
            if device == "pnp":
                temp_vc = vc
                vc = "-vc "
        else:
            if device == "pnp":
                vc = temp_vc
        max_location_vc = df_error[f"{vc}"][max_index]

        df_final_ = {'Run no.': f'{i}', 'Temp': f'{temp}', 'Device name': f'{device}', 'device': f'{list_devices[k]}','Simulated_Val':f'{Id_sim}','Mean error%':f'{"{:.2f}".format(mean_error)}', 'Max error%':f'{"{:.2f}".format(max_error)} @ {max_location_ib} & Vc (V) = {max_location_vc}'}
        df_final = df_final.append(df_final_, ignore_index = True)

    # Max mean error 
    print (df_final)   
    df_final.to_csv (f"{device}/Final_report_{Id_sim}.csv", index = False)
    out_report = pd.read_csv (f"{device}/Final_report_{Id_sim}.csv")
    print ("\n",f"Max. mean error = {out_report['Mean error%'].max()}%")    
    print ("=====================================================================================================================================================")

def main():

    # pandas setup 
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option("max_colwidth", None)
    pd.set_option('display.width', 1000)
    
    devices = ["npn","pnp"]
    list_devices = [["npn_10p00x10p00" , "npn_05p00x05p00" , "npn_00p54x16p00" , "npn_00p54x08p00" , "npn_00p54x04p00", "npn_00p54x02p00"],
                    ["pnp_10p00x00p42" , "pnp_05p00x00p42", "pnp_10p00x10p00" , "pnp_05p00x05p00"]]
    vc = ["vcp ","-vc (A)"]
    ib = ["ibp =","ib =-"]
    Id_sim  = "IcVc"
    sweep = [61,31] 
    step = [ "1.000E-06" ,  "3.000E-06" ,  "5.000E-06" ,  "7.000E-06" ,  "9.000E-06"] 

    for i, device in enumerate(devices): 
        # Folder structure of measured values 
        dirpath = f"{device}"
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
        os.makedirs(f"{device}/measured_{Id_sim}",exist_ok=False)

        # From xlsx to csv 
        read_file = pd.read_excel (f"../../180MCU_SPICE_DATA/BJT/bjt_{device}_icvc_f.nl_out.xlsx")
        read_file.to_csv (f"{device}/{device}.csv", index = False, header=True)

        # Folder structure of simulated values 
        os.makedirs(f"{device}/simulated_{Id_sim}",exist_ok=False)
        os.makedirs(f"{device}/error_{Id_sim}",exist_ok=False)

        # =========== Simulate ==============      
        ext_measured (device,vc[i],step,Id_sim,list_devices[i],ib[i])

        ext_simulated(device,vc[i],step,sweep[i],Id_sim,list_devices[i],ib[i])

        # ============ Results ============= 
        error_cal    (device,vc[i],step,Id_sim,list_devices[i],ib[i])

# ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================

if __name__ == "__main__":

    # Args
    arguments     = docopt(__doc__, version='comparator: 0.1')
    workers_count = os.cpu_count()*2 if arguments["--num_cores"] == None else int(arguments["--num_cores"])

    # Calling main function 
    main()
