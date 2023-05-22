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
# === CAP_MOS ===
NUM_DP_PER_TEMP_MOSCAP = 16


def moscap_meas_extraction(df: pd.DataFrame, dev_name: str):
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
    cj_cols = [c for c in df.columns if "Cj (fF)" in c]
    unwanted_cols = ['w', 'l', 'CV (fF)'] + dummy_cols + cj_cols

    # Cleanup dataframe from unwanted columns we don't use
    df = dataframe_cleanup(df, unwanted_cols)

    # For CAP_MOS 03v3/06v0, There are 144 variations = 4*4*3*3 [For device_type * W_L_variation * corners * temp]
    ## We have 4 types of CAP_MOS 03v3 [cap_nmos, cap_pmos, cap_nmos_b, cap_pmos_b]
    ## We have 4 W&L combination [(50, 50), (1, 1), (50, 1), (1, 50) um]
    ## We have 3 corners [typical, ff, ss]
    ## We have 3 temperature [25, -40, 175]

    all_temp = (
        [25] * NUM_DP_PER_TEMP_MOSCAP + [-40] * NUM_DP_PER_TEMP_MOSCAP + [175] * NUM_DP_PER_TEMP_MOSCAP
    )

    # Define new data frame that holds all variations
    dp_df = pd.DataFrame({'temp': all_temp})

    # "Unnamed: 2" cols: This column holds some info related to each device [name, W&L]
    ## Example nmoscap_3p3 (50u x50u )
    dp_df["device_name"] = df["Unnamed: 2"].apply(lambda x: x.split("\n")[0])
    dp_df["W (um)"] = df["Unnamed: 2"].apply(lambda x: x.split("\n")[1].split("x")[0].replace("(", "").replace("u", ""))
    dp_df["L (um)"] = df["Unnamed: 2"].apply(lambda x: x.split("\n")[1].split("x")[1].replace(")", "").replace("u", ""))
    dp_df["W (um)"] = dp_df["W (um)"].astype(float)
    dp_df["L (um)"] = dp_df["L (um)"].astype(float)

    # Cleanup dataframe from unwanted columns we don't use
    unwanted_cols = ['Unnamed: 2', 'corners']
    df = dataframe_cleanup(df, unwanted_cols)

    # Get number of columns that holds measurement data for each variation
    # Get columns names that holds data for each variation
    ## Using NUM_DP_PER_TEMP_MOSCAP * 3: As data is all 3 corners are combined in one table
    variations_count = NUM_DP_PER_TEMP_MOSCAP * 3
    num_data_col_per_dp, orig_col_names = get_orig_col_names(df, variations_count)

    # Generating all data points per each variation and combining all data in one DF
    all_dfs = []
    col_untouched = 'Vj'           # Name of column we don't need to touch it while stacking other columns
    stacked_col_name = 'corner'    # Name of new column in which we stacked other columns
    stacked_col_index = 'Cj'       # Name of column that holds all values of stacked columns

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
    all_dfs["device_name"] = all_dfs["device_name"].apply(lambda x: x.replace("nmoscap", "cap_nmos").replace("pmoscap", "cap_pmos"))
    all_dfs["device_name"] = all_dfs["device_name"].apply(lambda x: x.replace("3p3", "03v3").replace("6p0", "06v0"))

    ## Re-arranging columns of final data file
    all_dfs_cols = [
        "device_name",
        "W (um)",
        "L (um)",
        "corner",
        "temp",
        "Vj",
        "Cj",
    ]
    all_dfs = all_dfs.reindex(columns=all_dfs_cols)

    # Writing final dataframe that holds all clean data
    all_dfs.drop_duplicates(inplace=True)
    all_dfs.to_csv(f"{dev_name}_meas_cv.csv", index=False)
    logging.info(f"Full extracted measurement data for {dev_name}:\n {all_dfs}")
    logging.info(
        f"Full extracted measurement data for {dev_name} at: {dev_name}_meas_cv.csv"
    )
