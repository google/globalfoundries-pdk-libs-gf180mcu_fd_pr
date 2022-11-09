import pya
import sys
import os 
import pandas as pd 
import math

# Set device name form env. variable
device_pcell = device_in

# === Load gf180mcu pcells === 
technology_macros_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, technology_macros_path)

from cells import gf180mcu

# Instantiate and register the library
gf180mcu()

# Create new layout
layout = pya.Layout()

# Used db unit in gds file 
db_precession = 1000

# Create top cell
top = layout.create_cell("TOP")

# === Read gf180mcu pcells === 
lib = pya.Library.library_by_name("gf180mcu")

# ===== Draw function
def draw_pcell (device_name,device_space):
   
    # dnwell layer
    # dnwell         = layout.layer(12 , 0 )

    # Read csv file for bjt patterns
    df = pd.read_csv(f"patterns/{device_name}_patterns.csv")
    
    # Count num. of patterns [instances]
    patterns_no  = df.shape[0]
    pcell_row_no = int (math.sqrt(patterns_no)) 
    pcell_col_no = int (patterns_no/pcell_row_no)+1
    
    # inital value for instances location
    x_shift = 0
    y_shift = 0
    
    # Insert instance for each row
    for i, row in df.iterrows():
        
        # Get isntance location
        if (i % pcell_row_no) == 0:  x_shift = 0 if i == 0 else x_shift + device_space*db_precession
        
        if (i % pcell_row_no) == 0:  y_shift = 0 
        else:                        y_shift = 0 if i == 0 else y_shift + device_space*db_precession
         
        device,param = get_var (device_name,row)  

        pcell_id = lib.layout().pcell_id(device)
        
        pc = layout.add_pcell_variant(lib, pcell_id, param)        
        top.insert(pya.CellInstArray(pc, pya.Trans(x_shift,y_shift)))
        
        options = pya.SaveLayoutOptions()
        options.write_context_info = False
        layout.write(f"testcases/{device_name}_pcells.gds", options)
    
    # # draw dnwell for dw devices
    # if "_dn" in device: 
    #     bbox = str(layout.top_cell().dbbox()).replace("(","").replace(")","").replace(";",",").split(",")
    #     top.shapes(dnwell).insert(pya.Box(float(bbox[0])*db_precession, float(bbox[1])*db_precession , float(bbox[2])*db_precession, float(bbox[2])*db_precession))                              
    #     layout.write(f"testcases/{device_name}_dn_pcells.gds", options)
            
def get_var (device_name,row):
    
    if device_name == "bjt":
        device = row["device_name"]
        type   = row["Type"]
        param = {"Type": type}        

    elif "diode" in device_name:
        deepnwell   =  1
        pcmpgr      =  1
        if device_name == "diode_sc":
            device    = device_name 
            length     = row["length"]
            num_fing  = row["num_fing"]
            param = {"l":  length , "m":num_fing, "pcmpgr":  pcmpgr}
        elif "_dn" in device_name:
            device    = device_name.replace("_dn","")
            volt_area = row["volt"]
            length    = row["length"]
            width     = row["width"]
            param = {"volt": volt_area , "l": length , "w":  width, "pcmpgr":  pcmpgr, "deepnwell":  deepnwell}      
        else:
            device    = device_name
            volt_area = row["volt"]
            length    = row["length"]
            width     = row["width"]
            param = {"volt": volt_area , "l": length , "w":  width}        

    elif device_name == "MIM-A":
        device      = "cap_mim"
        length      = row["length"]
        width       = row["width"]
        param = {"mim_option": "MIM-A" , "l": length , "w":  width}   
       
    elif "MIM-B" in device_name:
        device      = "cap_mim"
        metal_level = row["metal_level"]
        length      = row["length"]
        width       = row["width"]
        param = {"mim_option": "MIM-B" , "metal_level": metal_level , "l": length , "w":  width} 
                    
    elif "cap_" in device_name and "mos" in device_name:
        if "_dn" in device_name:
            deepnwell   =  1
            pcmpgr      =  1
            device    = device_name.replace("_dn","")
            volt_area = row["volt"]
            length    = row["length"]
            width     = row["width"]
            param = {"volt": volt_area , "l": length , "w":  width, "deepnwell":  deepnwell, "pcmpgr":  pcmpgr}
        else:
            device    = device_name
            volt_area = row["volt"]
            length    = row["length"]
            width     = row["width"]
            param = {"volt": volt_area , "l": length , "w":  width}


    elif "resistor" in  device_name:
        if "high_Rs" in device_name:
            if "_dn" in device_name:
                deepnwell   =  1
                pcmpgr      =  1
                device    = device_name.replace("_dn","")
                volt_area = row["volt"]            
                length    = row["length"]
                width     = row["width"]
                param = {"volt": volt_area , "l": length , "w":  width, "deepnwell":  deepnwell, "pcmpgr":  pcmpgr}
            else:
                device    = device_name
                volt_area = row["volt"]            
                length    = row["length"]
                width     = row["width"]
                param = {"volt": volt_area , "l": length , "w":  width}       
        elif "metal_resistor" in device_name:
            device    = "metal_resistor"
            res_type  = row["res_type"]
            length    = row["length"]
            width     = row["width"]
            param = {"res_type": res_type , "l": length , "w":  width}
        elif "pwell" in device_name:
            pcmpgr      =  1
            device    = device_name            
            length    = row["length"]
            width     = row["width"]
            param = {"l": length , "w":  width, "pcmpgr":  pcmpgr}
        else:
            if "_dn" in device_name:
                deepnwell   =  1
                pcmpgr      =  1
                device    = device_name.replace("_dn","")            
                length    = row["length"]
                width     = row["width"]
                param = {"l": length , "w":  width, "deepnwell":  deepnwell, "pcmpgr":  pcmpgr}
            else:
                device    = device_name          
                length    = row["length"]
                width     = row["width"]
                param = {"l": length , "w":  width}     
            
    elif "nfet" in device_name and "10v0_asym" not in device_name and "cap_" not in device_name and "nvt" not in device_name and "_dn" not in device_name:
        device      = "nfet"
        device      = device_name
        volt_area   = row["volt"]
        width       = row["width"]        
        length      = row["length"]
        diff_length = row["l_diff"]
        num_fingers = row["num_fing"]
        bulk        = row["bulk"]
        param = {"volt": volt_area , "bulk": bulk, "w":  width , "l": length , "ld": diff_length , "nf": num_fingers}   

    elif "nfet" in device_name and "10v0_asym" not in device_name and "cap_" not in device_name and "nvt" not in device_name and "_dn" in device_name:
        device      = "nfet"
        device      = device_name.replace("_dn","")
        deepnwell   = 1
        pcmpgr      = 1
        volt_area   = row["volt"]
        width       = row["width"]        
        length      = row["length"]
        diff_length = row["l_diff"]
        num_fingers = row["num_fing"]
        bulk        = row["bulk"]
        param = {"deepnwell":deepnwell, "bulk": bulk, "volt": volt_area , "w":  width , "l": length , "ld": diff_length , "nf": num_fingers, "pcmpgr":  pcmpgr}

    elif "nvt" in device_name:
        device      = device_name
        width       = row["width"]        
        length      = row["length"]
        diff_length = row["l_diff"]
        num_fingers = row["num_fing"]
        bulk        = row["bulk"]
        param = {"w":  width , "l": length , "ld": diff_length , "nf": num_fingers, "bulk": bulk}
        
    elif "pfet" in device_name and "10v0_asym" not in device_name and "cap_" not in device_name and "_dn" not in device_name:
        device      = "pfet"
        # device      = device_name
        volt_area   = row["volt"]
        width       = row["width"]        
        length      = row["length"]
        diff_length = row["l_diff"]
        num_fingers = row["num_fing"]
        bulk        = row["bulk"]
        param = {"volt": volt_area, "bulk": bulk , "w":  width , "l": length , "ld": diff_length , "nf": num_fingers} 
    
    elif "pfet" in device_name and "10v0_asym" not in device_name and "cap_" not in device_name and "_dn" in device_name:
        device      = "pfet"
        # device      = device_name.replace("_dn","")
        deepnwell   = 1
        pcmpgr      = 1
        volt_area   = row["volt"]
        width       = row["width"]        
        length      = row["length"]
        diff_length = row["l_diff"]
        num_fingers = row["num_fing"]
        bulk        = row["bulk"]
        param = {"volt": volt_area, "bulk": bulk , "w":  width , "l": length , "ld": diff_length , "nf": num_fingers, "deepnwell":  deepnwell, "pcmpgr":  pcmpgr} 
    
    elif "10v0_asym" in device_name:
        device      = device_name
        width       = row["width"]        
        length      = row["length"]
        param = {"w":  width , "l": length} 
                         
    else:
        pass
    
    return device,param


# ======== BJT Gen. ========   

if device_pcell == "bjt":
    
    draw_pcell ("bjt",100)
    
# ======== Diode Gen. ========   

if "diode" in device_pcell:
    
    if "pw2dw" in device_pcell or "dw2ps" in device_pcell:
        draw_pcell (device_pcell,140)
    elif "_sc" in device_pcell:
        draw_pcell (device_pcell,200)
    else:
        draw_pcell (device_pcell,30)

# ======== cap_mim Gen. ========   

if "MIM" in device_pcell:
    draw_pcell (device_pcell,50)

# ======== FET Gen. ========   

if "fet" in device_pcell and "cap_" not in device_pcell:
    if "10v0_asym" in device_pcell or "nvt" in device_pcell:
        draw_pcell (device_pcell,450)
    else:
        draw_pcell (device_pcell,250)  
      
# ======== cap_mos Gen. ========   

if "mos" in device_pcell and "cap_" in device_pcell:
    draw_pcell (device_pcell,150)
    
# ======== RES Gen. ========   
    
if "resistor" in device_pcell:
    draw_pcell (device_pcell,50)
