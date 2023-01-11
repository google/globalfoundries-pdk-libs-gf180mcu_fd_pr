#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pandas as pd
import glob
from matplotlib import pyplot as plt
from matplotlib.ticker import EngFormatter
ROWS=67


def draw(measured,sim_path):
    """draw func draw measured data vs simulated data

    Args:
        measured (list[str]): measured files paths
        simulated (list[str]): simulated files paths
    """    
    print("measured is blue")
    print("simulated is red")
    df1 = pd.read_csv(measured)
    for i in range(int(len(df1)/ROWS)):
        df=pd.DataFrame()    
        space = sim_path[i].rfind("/")
        read_dev_name = sim_path[i][space + 1:]
        df1 = pd.read_csv(measured)
        df[0]=df1[df1.columns[0]][i*ROWS:(i+1)*ROWS]
        df[df1.columns[1:7]]=df1[df1.columns[1:7]][i*ROWS:(i+1)*ROWS]
        ax = df.plot(x=df.columns[0], y=df.columns[1:7], color="r", figsize=(15,12))
        volt_formatter = EngFormatter(unit='V')
        amp_formatter = EngFormatter(unit='A')
        ax.xaxis.set_major_formatter(volt_formatter)
        ax.yaxis.set_major_formatter(amp_formatter)
        df[0]=df1[df1.columns[0]][i*ROWS:(i+1)*ROWS]
        df[df1.columns[7:13]]=df1[df1.columns[7:13]][i*ROWS:(i+1)*ROWS]
        df.plot(ax=ax, x=df.columns[0], y=df.columns[7:13], color="b")
        plt.grid()
        plt.xlabel('Vds')
        plt.ylabel('Drain Current')
        plt.title(read_dev_name)        
    plt.show()

device =  [
        "nfet_03v3_iv",
        "pfet_03v3_iv",
        "nfet_06v0_iv",
        "pfet_06v0_iv",
        "nfet_06v0_nvt_iv",
        "nfet_03v3_dss_iv",
        "pfet_03v3_dss_iv",
        "nfet_06v0_dss_iv",
        "pfet_06v0_dss_iv"
    ]

dev=0
measured = (f"mos_iv_regr/{device[dev]}/error_analysis_Id.csv")
sim_path = glob.glob(f"mos_iv_regr/{device[dev]}/simulated_Id/*.csv")
draw(measured,sim_path)


# In[ ]:




