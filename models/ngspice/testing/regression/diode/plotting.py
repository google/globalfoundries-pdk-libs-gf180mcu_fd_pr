#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pandas as pd
import glob
from matplotlib import pyplot as plt
from matplotlib.ticker import EngFormatter


def draw(measured: list[str], simulated: list[str]) -> None:
    """draw func draw measured data vs simulated data

    Args:
        measured (list[str]): measured files paths
        simulated (list[str]): simulated files paths
    """
    print("measured is blue")
    print("simulated is red")
    measured.sort()
    simulated.sort()
    for i in range(len(measured)):
        space = measured[i].rfind("/")
        read_dev_name = measured[i][space + 1:]
        df = pd.read_csv(measured[i])
        ax = df.plot(x=df.columns[1], y=df.columns[2:], color="b", figsize=(15,12))
        volt_formatter = EngFormatter(unit='V')
        amp_formatter = EngFormatter(unit='fF')
        ax.xaxis.set_major_formatter(volt_formatter)
        ax.yaxis.set_major_formatter(amp_formatter)
        df = pd.read_csv(simulated[i])
        df.plot(ax=ax, x=df.columns[1], y=df.columns[2:], color="r")
        plt.title(read_dev_name)
        plt.grid()
        plt.xlabel('Voltage')
        plt.ylabel('Cv')
    plt.show()



device = [
    "diode_regr/diode_dw2ps",
    "diode_regr/diode_nd2ps_03v3",
    "diode_regr/diode_nd2ps_06v0",
    "diode_regr/diode_nw2ps_03v3",
    "diode_regr/diode_nw2ps_06v0",
    "diode_regr/diode_pd2nw_03v3",
    "diode_regr/diode_pd2nw_06v0",
    "diode_regr/diode_pw2dw",
    "diode_regr/sc_diode",
]

iv_cv_m = ["measured_iv", "measured_cv"]
iv_cv_s = ["simulated_iv", "simulated_cv"]
# 0 for diode_dw2ps
# 1 for diode_nd2ps_03v3
# 2 for diode_nd2ps_06v0
# 3 for diode_nw2ps_03v3
# 4 for diode_nw2ps_06v0
# 5 for diode_pd2nw_03v3
# 6 for diode_pd2nw_06v0
# 7 for diode_pw2dw
dev = 0

# 1 for cv 0 for iv
iv_cv = 1
measured = glob.glob(f"{device[dev]}/{iv_cv_m[iv_cv]}/*.csv")
simulated = glob.glob(f"{device[dev]}/{iv_cv_s[iv_cv]}/*.csv")
measured.sort()
simulated.sort()
# caling the draw func
draw(measured, simulated)


# In[ ]:


import os
import pandas as pd
import glob
from matplotlib import pyplot as plt
from matplotlib.ticker import EngFormatter


def draw(measured: list[str], simulated: list[str]) -> None:
    """draw func draw measured data vs simulated data

    Args:
        measured (list[str]): measured files paths
        simulated (list[str]): simulated files paths
    """
    print("measured is blue")
    print("simulated is red")
    measured.sort()
    simulated.sort()
    for i in range(len(measured)):
        space = measured[i].rfind("/")
        read_dev_name = measured[i][space + 1:]
        df = pd.read_csv(measured[i])
        ax = df.plot(x=df.columns[1], y=df.columns[2:], color="b", figsize=(15,12))
        volt_formatter = EngFormatter(unit='V')
        amp_formatter = EngFormatter(unit='A')
        ax.xaxis.set_major_formatter(volt_formatter)
        ax.yaxis.set_major_formatter(amp_formatter)
        df = pd.read_csv(simulated[i])
        df.plot(ax=ax, x=df.columns[1], y=df.columns[2:], color="r")
        plt.title(read_dev_name)
        plt.grid()
        plt.xlabel('Voltage')
        plt.ylabel('Iv')
        plt.show()



device = [
    "diode_regr/diode_dw2ps",
    "diode_regr/diode_nd2ps_03v3",
    "diode_regr/diode_nd2ps_06v0",
    "diode_regr/diode_nw2ps_03v3",
    "diode_regr/diode_nw2ps_06v0",
    "diode_regr/diode_pd2nw_03v3",
    "diode_regr/diode_pd2nw_06v0",
    "diode_regr/diode_pw2dw",
    "diode_regr/sc_diode",
]

iv_cv_m = ["measured_iv", "measured_cv"]
iv_cv_s = ["simulated_iv", "simulated_cv"]
# 0 for diode_dw2ps
# 1 for diode_nd2ps_03v3
# 2 for diode_nd2ps_06v0
# 3 for diode_nw2ps_03v3
# 4 for diode_nw2ps_06v0
# 5 for diode_pd2nw_03v3
# 6 for diode_pd2nw_06v0
# 7 for diode_pw2dw
dev = 0

# 1 for cv 0 for iv
iv_cv = 0
measured = glob.glob(f"{device[dev]}/{iv_cv_m[iv_cv]}/*.csv")
simulated = glob.glob(f"{device[dev]}/{iv_cv_s[iv_cv]}/*.csv")
measured.sort()
simulated.sort()
# caling the draw func
draw(measured, simulated)


# In[ ]:




