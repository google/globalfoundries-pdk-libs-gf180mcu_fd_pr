# Copyright 2023 GlobalFoundries PDK Authors
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

import pandas as pd
import logging
from utils import dataframe_cleanup, get_orig_col_names, stack_df_cols

# CONSTANT VALUES
## These values are manually selected after some analysis
## for provided measuremnet data.
# === BJT-IV ===
NUM_DP_PER_TEMP_NPN_IV = 6
NUM_DP_PER_TEMP_PNP_IV = 4


def bjt_iv_meas_extraction(df: pd.DataFrame, dev_name: str):
    """
    Function to extract measurement data for BJT-IV.

    Parameters
    ----------
    df : pd.dataframe
        Data frame for measured data provided by foundry
    dev_name : str
        Device we want to extract data for.
    Returns
    -------
       None
    """

    # Drop any unwanted columns
    ic_cols = [c for c in df.columns if "Ic (A)" in c]
    vep_cols = [c for c in df.columns if "vep=0" in c]
    ve_cols = [c for c in df.columns if "ve=-0" in c]
    unwanted_cols = ['W (um)', 'Ids'] + ic_cols + vep_cols + ve_cols

    # Cleanup dataframe from unwanted columns we don't use
    df = dataframe_cleanup(df, unwanted_cols)

    # For BJT npn devices, There are 24 variations = 6*4 [For W_L_variation * temp]
    # For BJT pnp devices, There are 16 variations = 4*4 [For W_L_variation * temp]
    ## We have 4 temperature [25, -40, 125, 175]

    NUM_DP_PER_TEMP_IV = NUM_DP_PER_TEMP_NPN_IV if 'npn' in dev_name else NUM_DP_PER_TEMP_PNP_IV

    all_temp = (
        [25] * NUM_DP_PER_TEMP_IV + [-40] * NUM_DP_PER_TEMP_IV + [125] * NUM_DP_PER_TEMP_IV + [175] * NUM_DP_PER_TEMP_IV
    )

    # Define new data frame that holds all variations
    dp_df = pd.DataFrame({'temp': all_temp})

    # "Unnamed: 2" cols: This column holds some info related to each device [name, W&L]
    ## Example vnpn_10x10 (u xu ,  nf=1,  m=1)
    dp_df["device_name"] = df["Unnamed: 2"].astype(str).apply(lambda x: x.split("\n")[0])
    dp_df["corner"] = df["corners"].copy()
    # Cleanup dataframe from unwanted columns we don't use
    unwanted_cols = ['Unnamed: 2', 'corners']
    df = dataframe_cleanup(df, unwanted_cols)

    # Get number of columns that holds measurement data for each variation
    # Get columns names that holds data for each variation
    num_data_col_per_dp, orig_col_names = get_orig_col_names(df, NUM_DP_PER_TEMP_IV * 4)

    # Generating all data points per each variation and combining all data in one DF
    all_dfs = []
    # Name of column we don't need to touch it while stacking other columns
    col_untouched = 'vcp (A)' if 'npn' in dev_name else '-vc (A)'
    stacked_col_name = 'ibp'       # Name of new column in which we stacked other columns
    stacked_col_index = 'ic'       # Name of column that holds all values of stacked columns

    for i in range(0, len(df.columns), num_data_col_per_dp):
        sub_df = df[df.columns[i : i + num_data_col_per_dp]].copy()
        sub_df.columns = orig_col_names
        stacked_corner_df = stack_df_cols(sub_df, col_untouched, stacked_col_name, stacked_col_index)
        for c in dp_df.columns:
            stacked_corner_df[c] = dp_df.loc[len(all_dfs), c]
        all_dfs.append(stacked_corner_df)

    all_dfs = pd.concat(all_dfs)
    all_dfs.drop_duplicates(inplace=True)

    # Cleaning some columns and values to match latest version of GF180MCU models
    if 'npn' in dev_name:
        all_dfs.rename(columns={'vcp (A)': 'vcp'}, inplace=True)
    else:
        all_dfs.rename(columns={'-vc (A)': 'vcp'}, inplace=True)
        all_dfs["vcp"] = all_dfs["vcp"].apply(lambda x: x * -1)
        all_dfs["ic"] = all_dfs["ic"].apply(lambda x: x * -1)

    all_dfs["device_name"] = all_dfs["device_name"].apply(lambda x: x.replace("vnpn", "npn").replace("vpnp", "pnp"))
    all_dfs["device_name"] = all_dfs["device_name"].apply(lambda x: x.replace("10x10", "10p00x10p00").replace("5x5", "05p00x05p00"))
    all_dfs["device_name"] = all_dfs["device_name"].apply(lambda x: x.replace("0p54x16", "00p54x16p00").replace("0p54x8", "00p54x08p00"))
    all_dfs["device_name"] = all_dfs["device_name"].apply(lambda x: x.replace("0p54x4", "00p54x04p00").replace("0p54x2", "00p54x02p00"))
    all_dfs["device_name"] = all_dfs["device_name"].apply(lambda x: x.replace("0p42x10", "10p00x00p42").replace("0p42x5", "05p00x00p42"))
    all_dfs["ibp"] = all_dfs["ibp"].apply(lambda x: x.split("=")[1])
    all_dfs["ibp"] = all_dfs["ibp"].astype(float)

    # Generiting sweep file for BJT-iv devices
    gen_bjt_iv_sweeps(all_dfs, dev_name)

    ## Re-arranging columns of final data file
    all_dfs_cols = [
        "device_name",
        "corner",
        "temp",
        "ibp",
        "vcp",
        "ic",
    ]
    all_dfs = all_dfs.reindex(columns=all_dfs_cols)

    # Writing final dataframe that holds all clean data
    all_dfs.drop_duplicates(inplace=True)
    all_dfs.to_csv(f"{dev_name}_iv_meas.csv", index=False)
    logging.info(f"Full extracted measurement data for {dev_name}:\n {all_dfs}")
    logging.info(
        f"Full extracted measurement data for {dev_name} at: {dev_name}_iv_meas.csv"
    )


def gen_bjt_iv_sweeps(df: pd.DataFrame, dev_name: str):
    """
    Function to generate sweeps for MOSCAP devices.

    Parameters
    ----------
    df : pd.dataframe
        Data frame for all extracted measured data points.
    dev_name : str
        Device we want to extract data for.
    Returns
    -------
       None
    """

    sweeps_df = df.copy()
    min_volt_val = sweeps_df['vcp'].min()
    max_volt_val = sweeps_df['vcp'].max()
    step_volt_val = round(sweeps_df['vcp'].diff().max(), 2) if 'npn' in dev_name else abs(round(sweeps_df['vcp'].diff().min(), 2))

    min_curr_val = sweeps_df['ibp'].min()
    max_curr_val = sweeps_df['ibp'].max()
    step_curr_val = round(sweeps_df['ibp'].diff().max(), 6) if 'npn' in dev_name else abs(round(sweeps_df['ibp'].diff().min(), 6))

    sweeps_df.drop(['vcp', 'ibp', 'ic'], axis=1, inplace=True)
    sweeps_df.drop_duplicates(inplace=True)
    sweeps_df['sweep'] = f'Vcp {min_volt_val} {max_volt_val} {step_volt_val} Ib {min_curr_val} {max_curr_val} {step_curr_val}'

    ## Re-arranging columns of final data file
    sweeps_df_cols = [
        "device_name",
        "corner",
        "temp",
        "sweep",
    ]
    sweeps_df = sweeps_df.reindex(columns=sweeps_df_cols)

    # Writing final dataframe that holds all clean data
    sweeps_df.to_csv(f"{dev_name}_iv_sweeps.csv", index=False)
    logging.info(f"Sweep data points for {dev_name}:\n {sweeps_df}")
    logging.info(f"Number of sweep points for {dev_name}: {len(sweeps_df)}")
    logging.info(f"Extracted sweep measurement data for {dev_name} at : {dev_name}_iv_sweeps.csv")
