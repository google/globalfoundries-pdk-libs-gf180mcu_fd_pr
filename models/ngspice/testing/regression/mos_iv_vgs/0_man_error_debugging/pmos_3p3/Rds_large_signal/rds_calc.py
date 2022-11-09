import pandas as pd


df = pd.read_csv ("../../../pfet_03v3_iv/simulated_Id/0_simulated_W10_L10.0.csv")

df["vgs =-0.8"] = df["-vds (V)"]/df["vgs =-0.8"]
df["vgs =-1.3"] = df["-vds (V)"]/df["vgs =-1.3"]
df["vgs =-1.8"] = df["-vds (V)"]/df["vgs =-1.8"]
df["vgs =-2.3"] = df["-vds (V)"]/df["vgs =-2.3"]
df["vgs =-2.8"] = df["-vds (V)"]/df["vgs =-2.8"]
df["vgs =-3.3"] = df["-vds (V)"]/df["vgs =-3.3"]

df.to_csv ("0_simulated_W10_L10.0.csv")

