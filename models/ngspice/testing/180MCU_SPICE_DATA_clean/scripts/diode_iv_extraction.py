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
# === diode_IV ===
NUM_DP_PER_VAR = 8


def diode_iv_meas_extraction(df: pd.DataFrame, dev_name: str):
    """
    Function to extract measurement data for MOSCAP.

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
    dummy_cols = [c for c in df.columns if "dummy_" in c]
    cj_cols = [c for c in df.columns if "In1(A)" in c and "diode" not in c]
    unwanted_cols = (
        ["Area", "Pj", "Ion (A/um²) @V=Von", "Ioff (pA/um²) @V=-Vdd"]
        + dummy_cols
        + cj_cols
    )

    # Cleanup dataframe from unwanted columns we don't use
    df = dataframe_cleanup(df, unwanted_cols)

    # For diode, There are 24 variations = 2*4*3 [For A_P_variation * temp * corners]
    ## We have 4 A&P  combination [(100, 40), (50, 102) um]
    ## We have 3 corners [typical, ff, ss]
    ## We have 3 temperature [-40, 25, 125, 175]
    all_temp = [-40] + [25] + [125] + [175] + [-40] + [25] + [125] + [175]

    # Define new data frame that holds all variations
    dp_df = pd.DataFrame({"temp": all_temp})

    # "Unnamed: 2" cols: This column holds some info related to each device [name, W&L]
    ## Example dnwps (100u x40u ,  nf=1,  m=1)
    dp_df["Area (pm^2)"] = df["Unnamed: 2"][df["Unnamed: 2"].notnull()].apply(
        lambda x: x.split("\n")[1].split("x")[0].replace("(", "").replace("u", "")
    )
    dp_df["Pj (um)"] = df["Unnamed: 2"][df["Unnamed: 2"].notnull()].apply(
        lambda x: x.split("\n")[1].split("x")[1].split("u")[0]
    )
    dp_df["Area (pm^2)"] = dp_df["Area (pm^2)"].astype(float)
    dp_df["Pj (um)"] = dp_df["Pj (um)"].astype(float)

    # Cleanup dataframe from unwanted columns we don't use
    unwanted_cols = ["Unnamed: 2", "corners"]
    df = dataframe_cleanup(df, unwanted_cols)

    # Get number of columns that holds measurement data for each variation
    # Get columns names that holds data for each variation
    ## Using NUM_DP_PER_CORNER * 3: As data is all 3 corners are combined in one table
    num_data_col_per_dp, orig_col_names = get_orig_col_names(df, NUM_DP_PER_VAR)

    # Generating all data points per each variation and combining all data in one DF
    all_dfs = []
    col_untouched = "Vn1 (V)"  # Name of column we don't need to touch it while stacking other columns
    stacked_col_name = "corner"  # Name of new column in which we stacked other columns
    stacked_col_index = (
        "In1(A)"  # Name of column that holds all values of stacked columns
    )

    for i in range(0, len(df.columns), num_data_col_per_dp):
        sub_df = df[df.columns[i : i + num_data_col_per_dp]].copy()
        sub_df.columns = orig_col_names
        stacked_corner_df = stack_df_cols(
            sub_df, col_untouched, stacked_col_name, stacked_col_index
        )
        for c in dp_df.columns:
            stacked_corner_df[c] = dp_df.loc[len(all_dfs), c]
        all_dfs.append(stacked_corner_df)

    all_dfs = pd.concat(all_dfs)
    all_dfs.drop_duplicates(inplace=True)

    # Cleaning corner column to use same name in GF180MCU models
    all_dfs["corner"] = all_dfs["corner"].apply(lambda x: x.split(" ")[-1])

    # Generiting sweep file for Diode-iv devices
    gen_diode_iv_sweeps(all_dfs, dev_name)

    ## Re-arranging columns of final data file
    all_dfs_cols = [
        "Area (pm^2)",
        "Pj (um)",
        "corner",
        "temp",
        "Vn1 (V)",
        "In1(A)",
    ]
    all_dfs = all_dfs.reindex(columns=all_dfs_cols)
    all_dfs = all_dfs.rename(columns={"In1(A)": "In", "Vn1 (V)": "Vn"})

    # Writing final dataframe that holds all clean data
    all_dfs.drop_duplicates(inplace=True)
    all_dfs.to_csv(f"{dev_name}_iv_meas.csv", index=False)
    logging.info(f"Full extracted measurement data for {dev_name}:\n {all_dfs}")
    logging.info(
        f"Full extracted measurement data for {dev_name} at: {dev_name}_iv_meas.csv"
    )


def gen_diode_iv_sweeps(df: pd.DataFrame, dev_name: str):
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
    min_volt_val = sweeps_df["Vn1 (V)"].min()
    max_volt_val = sweeps_df["Vn1 (V)"].max()
    step_volt_val = abs(round(sweeps_df["Vn1 (V)"].diff().max(), 2))

    sweeps_df.drop(["Vn1 (V)", "In1(A)"], axis=1, inplace=True)
    sweeps_df.drop_duplicates(inplace=True)
    sweeps_df["sweep"] = f"Vn {min_volt_val} {max_volt_val} {step_volt_val}"

    ## Re-arranging columns of final data file
    sweeps_df_cols = [
        "Area (pm^2)",
        "Pj (um)",
        "corner",
        "temp",
        "sweep",
    ]
    sweeps_df = sweeps_df.reindex(columns=sweeps_df_cols)

    # Writing final dataframe that holds all clean data
    sweeps_df.to_csv(f"{dev_name}_iv_sweeps.csv", index=False)
    logging.info(f"Sweep data points for {dev_name}:\n {sweeps_df}")
    logging.info(f"Number of sweep points for {dev_name}: {len(sweeps_df)}")
    logging.info(
        f"Extracted sweep measurement data for {dev_name} at : {dev_name}_iv_sweeps.csv"
    )
