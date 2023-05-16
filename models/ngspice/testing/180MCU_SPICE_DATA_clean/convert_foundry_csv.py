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
"""
Usage:
  convert_foundry_csv.py --excel_path=<path> --device_type=<device_type>

  --excel_path=<path>             Excel path for measured data
  --device_type=<device_type>     Name of device for extracted data 
  -h, --help                      Show help text.
  -v, --version                   Show version.
"""

from docopt import docopt
import pandas as pd
import numpy as np
import os
import glob
import logging

# CONSTANTS
NUM_DP_PER_TEMP = 25
NUM_COLS_MEAS_VBS = 7
NUM_COLS_MEAS_VGS = 8


def parse_dp_id_vgs_vbs(sub_df):
    """
    Function to parse measurement data for Ids Vs Vgs with Vbs sweep to be used in simulation.

    Parameters
    ----------
    sub_df : pd.DataFrame
        DataFrame that holds sub measurement information per each variation.
    """

    ## Id Vs Vgs [Vbs sweep]
    df_id_vgs_vbs = sub_df.iloc[:, :NUM_COLS_MEAS_VBS]
    vds_df_id_vgs_vbs = float(df_id_vgs_vbs.columns[0].split("/")[0].split("=")[1])
    df_id_vgs_vbs.drop(columns=df_id_vgs_vbs.columns[0], inplace=True)

    # Get vgs sweep values
    vgs_min_val = df_id_vgs_vbs["vgs "].min()
    vgs_max_val = df_id_vgs_vbs["vgs "].max()
    vgs_step_val = abs(df_id_vgs_vbs["vgs "][1] - df_id_vgs_vbs["vgs "][0])

    df_id_vgs_vbs = (
        df_id_vgs_vbs.set_index(["vgs "])
        .stack()
        .reset_index(name=f"id")
        .rename(columns={"level_1": "vbs"})
        .rename(columns={"vgs ": "vgs"})
    )

    df_id_vgs_vbs["vbs"] = df_id_vgs_vbs["vbs"].apply(lambda x: x.split("=")[1])
    df_id_vgs_vbs["vbs"] = df_id_vgs_vbs["vbs"].astype(float)
    df_id_vgs_vbs["vds"] = vds_df_id_vgs_vbs
    df_id_vgs_vbs["rds"] = np.nan
    df_id_vgs_vbs["const_var"] = "vds"
    df_id_vgs_vbs["const_var_val"] = vds_df_id_vgs_vbs
    df_id_vgs_vbs["out_col"] = "id"

    # Get vgs sweep values
    vbs_min_val = df_id_vgs_vbs["vbs"].min()
    vbs_max_val = df_id_vgs_vbs["vbs"].max()
    vbs_step_val = abs(df_id_vgs_vbs["vbs"][1] - df_id_vgs_vbs["vbs"][0])

    df_id_vgs_vbs[
        "sweeps"
    ] = f"vgs {vgs_min_val} {vgs_max_val} {vgs_step_val} vbs {vbs_min_val} {vbs_max_val} {vbs_step_val}"

    cols_order_group = [
        "vds",
        "vgs",
        "vbs",
        "id",
        "rds",
        "const_var",
        "const_var_val",
        "sweeps",
        "out_col",
    ]
    df_id_vgs_vbs = df_id_vgs_vbs.reindex(columns=cols_order_group)

    return df_id_vgs_vbs


def parse_dp_id_vds_vgs(sub_df):
    """
    Function to parse measurement data for Ids Vs Vds with Vgs sweep to be used in simulation.

    Parameters
    ----------
    sub_df : pd.DataFrame
        DataFrame that holds sub measurement information per each variation.
    """

    ## Id Vs Vds [Vgs sweep]
    df_id_vds_vgs = sub_df.iloc[
        :, NUM_COLS_MEAS_VBS : NUM_COLS_MEAS_VBS + NUM_COLS_MEAS_VGS
    ]
    vbs_df_id_vds_vgs = float(df_id_vds_vgs.columns[0].split("/")[0].split("=")[1])
    df_id_vds_vgs.drop(columns=df_id_vds_vgs.columns[0], inplace=True)

    # Get vds sweep values
    vds_min_val = df_id_vds_vgs["vds (V)"].min()
    vds_max_val = df_id_vds_vgs["vds (V)"].max()
    vds_step_val = abs(df_id_vds_vgs["vds (V)"][1] - df_id_vds_vgs["vds (V)"][0])

    df_id_vds_vgs = (
        df_id_vds_vgs.set_index(["vds (V)"])
        .stack()
        .reset_index(name=f"id")
        .rename(columns={"level_1": "vgs"})
        .rename(columns={"vds (V)": "vds"})
    )

    df_id_vds_vgs["vgs"] = df_id_vds_vgs["vgs"].apply(lambda x: x.split("=")[1])
    df_id_vds_vgs["vgs"] = df_id_vds_vgs["vgs"].astype(float)
    df_id_vds_vgs["vbs"] = vbs_df_id_vds_vgs
    df_id_vds_vgs["rds"] = np.nan
    df_id_vds_vgs["const_var"] = "vbs"
    df_id_vds_vgs["const_var_val"] = vbs_df_id_vds_vgs
    df_id_vds_vgs["out_col"] = "id"

    # Get vgs sweep values
    vgs_min_val = df_id_vds_vgs["vgs"].min()
    vgs_max_val = df_id_vds_vgs["vgs"].max()
    vgs_step_val = abs(df_id_vds_vgs["vgs"][1] - df_id_vds_vgs["vgs"][0])

    df_id_vds_vgs[
        "sweeps"
    ] = f"vds {vds_min_val} {vds_max_val} {vds_step_val} vgs {vgs_min_val} {vgs_max_val} {vgs_step_val}"

    cols_order_group = [
        "vds",
        "vgs",
        "vbs",
        "id",
        "rds",
        "const_var",
        "const_var_val",
        "sweeps",
        "out_col",
    ]
    df_id_vds_vgs = df_id_vds_vgs.reindex(columns=cols_order_group)

    df_id_vds_vgs.to_csv("df_id_vds_vgs.csv")
    return df_id_vds_vgs


def parse_dp_rds_vds_vgs(sub_df):
    """
    Function to parse measurement data for Rds Vs Vds with Vgs sweep to be used in simulation.

    Parameters
    ----------
    sub_df : pd.DataFrame
        DataFrame that holds sub measurement information per each variation.
    """

    ## Rds Vs Vds [Vgs sweep]
    df_rds_vds_vgs = sub_df.iloc[:, -NUM_COLS_MEAS_VGS:]

    vbs_df_rds_vds_vgs = float(df_rds_vds_vgs.columns[0].split("/")[0].split("=")[1])
    df_rds_vds_vgs.drop(columns=df_rds_vds_vgs.columns[0], inplace=True)

    # Get vds sweep values
    vds_min_val = df_rds_vds_vgs["vds (V).1"].min()
    vds_max_val = df_rds_vds_vgs["vds (V).1"].max()
    vds_step_val = abs(df_rds_vds_vgs["vds (V).1"][1] - df_rds_vds_vgs["vds (V).1"][0])

    df_rds_vds_vgs = (
        df_rds_vds_vgs.set_index(["vds (V).1"])
        .stack()
        .reset_index(name=f"rds")
        .rename(columns={"level_1": "vgs"})
        .rename(columns={"vds (V).1": "vds"})
    )

    df_rds_vds_vgs["vgs"] = df_rds_vds_vgs["vgs"].apply(
        lambda x: ".".join(x.split("=")[1].split(".")[:2])
    )
    df_rds_vds_vgs["vgs"] = df_rds_vds_vgs["vgs"].astype(float)
    df_rds_vds_vgs["vbs"] = vbs_df_rds_vds_vgs
    df_rds_vds_vgs["id"] = np.nan
    df_rds_vds_vgs["const_var"] = "vbs"
    df_rds_vds_vgs["const_var_val"] = vbs_df_rds_vds_vgs
    df_rds_vds_vgs["out_col"] = "rds"

    # Get vgs sweep values
    vgs_min_val = df_rds_vds_vgs["vgs"].min()
    vgs_max_val = df_rds_vds_vgs["vgs"].max()
    vgs_step_val = abs(df_rds_vds_vgs["vgs"][1] - df_rds_vds_vgs["vgs"][0])

    df_rds_vds_vgs[
        "sweeps"
    ] = f"vds {vds_min_val} {vds_max_val} {vds_step_val} vgs {vgs_min_val} {vgs_max_val} {vgs_step_val}"

    cols_order_group = [
        "vds",
        "vgs",
        "vbs",
        "id",
        "rds",
        "const_var",
        "const_var_val",
        "sweeps",
        "out_col",
    ]
    df_rds_vds_vgs = df_rds_vds_vgs.reindex(columns=cols_order_group)

    return df_rds_vds_vgs


def parse_dp_sweeps(sub_df):
    """
    Function to parse measurement data to be used in simulation.

    Parameters
    ----------
    sub_df : pd.DataFrame
        DataFrame that holds sub measurement information per each variation.
    """

    ## Id Vs Vgs [Vbs sweep]
    df_id_vgs_vbs = parse_dp_id_vgs_vbs(sub_df)

    ## Id Vs Vds [Vgs sweep]
    df_id_vds_vgs = parse_dp_id_vds_vgs(sub_df)

    ## Rds Vs Vds [Vgs sweep]
    df_rds_vds_vgs = parse_dp_rds_vds_vgs(sub_df)

    df_dp_sweeps = pd.concat([df_id_vgs_vbs, df_id_vds_vgs, df_rds_vds_vgs])

    return df_dp_sweeps


def fet_meas_extraction(df, dev_name):
    """
    Function to extract measurement data for Fets.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame that holds all the measurement information for selected fet.
    dev_name : str
        Device we want to extract data for.
    """

    # Get the columns with only NaN values
    nan_columns = df.columns[df.isna().all()]
    # Drop the columns with only NaN values
    df.drop(columns=nan_columns, inplace=True)

    variations_count = df["L (um)"].count()

    logging.info(f"No of variations are {variations_count}")
    logging.info(f"Length of data points is {len(df.columns)}")

    # There are 75 variations = 25*3 [For each temp] and all variations are extracted at tt corner
    ## Please note that the temp variation wasn't included in dataset so we will have to add that new column
    all_temp = (
        [25] * NUM_DP_PER_TEMP + [-40] * NUM_DP_PER_TEMP + [125] * NUM_DP_PER_TEMP
    )

    ## TODO: This variable will need to be changed based on device type
    id_cols = [c for c in df.columns if "Id (A)" in c]
    rd_cols = [c for c in df.columns if "Rds" in c]
    unwanted_cols = ["Unnamed: 2", "Ids"] + id_cols + rd_cols
    df.drop(columns=unwanted_cols, inplace=True)

    dp_cols = ["W (um)", "L (um)", "corners"]
    dp_df = df[dp_cols].iloc[:variations_count].copy()
    dp_df["temp"] = all_temp
    df.drop(columns=dp_cols, inplace=True)

    num_data_col_per_dp = int(len(df.columns) / variations_count)
    orig_col_names = df.columns[:num_data_col_per_dp]

    logging.info(f" Data points :\n {dp_df}")
    logging.info(f" Length of data points :\n {len(dp_df)}")
    logging.info(f" No of data columns :\n {len(df.columns)}")
    logging.info(f" No of data columns per variation:\n {num_data_col_per_dp}")
    logging.info(f" Original columns per variation:\n {orig_col_names}")

    all_dfs = []
    for i in range(0, len(df.columns), num_data_col_per_dp):
        sub_df = df[df.columns[i : i + num_data_col_per_dp]].copy()
        sub_df.columns = orig_col_names
        parsed_df = parse_dp_sweeps(sub_df)
        for c in dp_df.columns:
            parsed_df[c] = dp_df.loc[len(all_dfs), c]
        all_dfs.append(parsed_df)

    all_dfs = pd.concat(all_dfs)
    all_dfs.drop_duplicates(inplace=True)
    all_dfs.rename(columns={"corners": "corner"}, inplace=True)
    all_dfs_cols = [
        "W (um)",
        "L (um)",
        "corner",
        "temp",
        "vds",
        "vgs",
        "vbs",
        "id",
        "rds",
        "const_var",
        "const_var_val",
        "sweeps",
        "out_col",
    ]
    all_dfs = all_dfs.reindex(columns=all_dfs_cols)

    logging.info(f"Length of all data points {len(all_dfs)}")

    for c in all_dfs.columns:
        logging.info(f"col: {c} has nan: {all_dfs[c].isna().any()}")

    ## Generate csv file contains simulation sweeps
    sweeps_df = all_dfs[
        [
            "W (um)",
            "L (um)",
            "corner",
            "temp",
            "const_var",
            "const_var_val",
            "sweeps",
            "out_col",
        ]
    ].copy()

    sweeps_df.drop_duplicates(inplace=True)
    sweeps_df.to_csv(f"{dev_name}_sweeps.csv")
    logging.info(f"Sweep csv file for {dev_name}: {sweeps_df}")
    logging.info(f"Sweep csv file for {dev_name} at : {sweeps_df}_sweeps.csv")

    all_dfs.drop_duplicates(inplace=True)
    all_dfs.to_csv(f"{dev_name}_meas.csv", index=False)
    logging.info(f"Full extracted measurement data for {dev_name}: {sweeps_df}")
    logging.info(
        f"Full extracted measurement data for {dev_name} at: {dev_name}_meas.csv"
    )


def main(args):
    """
    main function to extract measurement data for GF180MCU models.

    Parameters
    ----------
    arguments : dict
        Dictionary that holds the arguments used by user in the run command. This is generated by docopt library.
    """

    excel_path = args["--excel_path"]
    dev_type = args["--device_type"]

    if not os.path.exists(excel_path) or not os.path.isfile(excel_path):
        logging.error(
            f"Provided {excel_path} excel sheet doesn't exist, please recheck"
        )
        exit(1)

    if "fet" in dev_type:
        df = pd.read_excel(excel_path)
        fet_meas_extraction(df, dev_type)
    else:
        logging.error("Suported devices are: Fets")
        exit(1)


if __name__ == "__main__":

    # Args
    arguments = docopt(__doc__, version="DATA EXTRACTOR: 0.1")

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[logging.StreamHandler(),],
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Calling main function
    main(arguments)
