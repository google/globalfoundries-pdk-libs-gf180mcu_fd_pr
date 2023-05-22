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
from utils import dataframe_cleanup, get_orig_col_names, get_variation_count

# CONSTANT VALUES
## These values are manually selected after some analysis
## for provided measuremnet data.
# === FETS-IV ===
NUM_COLS_MEAS_VBS_03v3 = 7
NUM_COLS_MEAS_VBS_06v0 = 6
NUM_COLS_MEAS_VDS_CV = 3
NUM_COLS_MEAS_VGS_CV = 6


def parse_cgd_vds_vgs(sub_df, dev_type, dev_name):
    """
    Function to parse measurement data for Cgd Vs Vds with Vgs sweep to be used in simulation.

    Parameters
    ----------
    sub_df : pd.DataFrame
        DataFrame that holds sub measurement information per each variation.
    dev_type : str
        Type of device we want to extract data for [nfet or pfet].
    dev_name : str
        Device we want to extract data for.
    Returns
    ----------
    df_cgd_vds_vgs : pd.DataFrame
        DataFrame that holds all measurement points for Cgd Vs Vds with Vgs sweep
    """

    # Get no of cols per variation for vbs sweep
    NUM_COLS_MEAS_VBS = NUM_COLS_MEAS_VBS_03v3 if '03v3' in dev_name else NUM_COLS_MEAS_VBS_06v0

    ## Cgc Vs Vds [Vgs sweep]
    df_cgd_vds_vgs = sub_df.iloc[
        :, NUM_COLS_MEAS_VBS + NUM_COLS_MEAS_VDS_CV + NUM_COLS_MEAS_VGS_CV : NUM_COLS_MEAS_VBS + NUM_COLS_MEAS_VDS_CV + 2 * NUM_COLS_MEAS_VGS_CV
    ]

    vbs_df_cgd_vds_vgs = float(df_cgd_vds_vgs.columns[0].split("/")[0].split("=")[1])
    df_cgd_vds_vgs.drop(columns=df_cgd_vds_vgs.columns[0], inplace=True)

    # Get vgs sweep values
    vds_col_name = "Vds (V).1"

    # Get Vgs step value
    vds_step_val = round(abs(df_cgd_vds_vgs[vds_col_name][1] - df_cgd_vds_vgs[vds_col_name][0]), 2)

    # Stacking all vbs sweeps in one column
    df_cgd_vds_vgs = (
        df_cgd_vds_vgs.set_index([vds_col_name])
        .stack()
        .reset_index(name="cgd")
        .rename(columns={"level_1": "vgs"})
        .rename(columns={vds_col_name: "vds"})
    )

    # Multiplying vgs by -1 for pfet devices to match provided data
    df_cgd_vds_vgs["vds"] = df_cgd_vds_vgs["vds"].apply(lambda x: x * -1) if "pfet" in dev_type else df_cgd_vds_vgs["vds"]

    # Get min/max values of vgs sweep
    vds_min_val = df_cgd_vds_vgs["vds"].min()
    vds_max_val = df_cgd_vds_vgs["vds"].max()

    # Adding columns for all voltage sweeps and output
    df_cgd_vds_vgs["vgs"] = df_cgd_vds_vgs["vgs"].apply(
        lambda x: ".".join(x.split("=")[1].split(".")[:2])
    )
    df_cgd_vds_vgs["vgs"] = df_cgd_vds_vgs["vgs"].astype(float)
    df_cgd_vds_vgs["vbs"] = vbs_df_cgd_vds_vgs
    df_cgd_vds_vgs["const_var"] = "vbs"
    df_cgd_vds_vgs["const_var_val"] = vbs_df_cgd_vds_vgs
    df_cgd_vds_vgs["out_col"] = "cgd"

    # Get vds sweep values
    vgs_min_val = df_cgd_vds_vgs["vgs"].min()
    vgs_max_val = df_cgd_vds_vgs["vgs"].max()
    vgs_step_val = abs(df_cgd_vds_vgs["vgs"][1] - df_cgd_vds_vgs["vgs"][0])

    # Adding sweeps used per each variation
    df_cgd_vds_vgs[
        "sweeps"
    ] = f"vds {vds_min_val} {vds_max_val} {vds_step_val} vgs {vgs_min_val} {vgs_max_val} {vgs_step_val}"

    return df_cgd_vds_vgs


def parse_cgs_vds_vgs(sub_df, dev_type, dev_name):
    """
    Function to parse measurement data for Cgs Vs Vds with Vgs sweep to be used in simulation.

    Parameters
    ----------
    sub_df : pd.DataFrame
        DataFrame that holds sub measurement information per each variation.
    dev_type : str
        Type of device we want to extract data for [nfet or pfet].
    dev_name : str
        Device we want to extract data for.
    Returns
    ----------
    df_cgs_vds_vgs : pd.DataFrame
        DataFrame that holds all measurement points for Cgs Vs Vds with Vgs sweep
    """

    # Get no of cols per variation for vbs sweep
    NUM_COLS_MEAS_VBS = NUM_COLS_MEAS_VBS_03v3 if '03v3' in dev_name else NUM_COLS_MEAS_VBS_06v0

    ## Cgc Vs Vds [Vgs sweep]
    df_cgs_vds_vgs = sub_df.iloc[
        :, NUM_COLS_MEAS_VBS + NUM_COLS_MEAS_VDS_CV : NUM_COLS_MEAS_VBS + NUM_COLS_MEAS_VDS_CV + NUM_COLS_MEAS_VGS_CV
    ]

    vbs_df_cgs_vds_vgs = float(df_cgs_vds_vgs.columns[0].split("/")[0].split("=")[1])
    df_cgs_vds_vgs.drop(columns=df_cgs_vds_vgs.columns[0], inplace=True)

    # Get vgs sweep values
    vds_col_name = "Vds (V)"

    # Get Vgs step value
    vds_step_val = round(abs(df_cgs_vds_vgs[vds_col_name][1] - df_cgs_vds_vgs[vds_col_name][0]), 2)

    # Stacking all vbs sweeps in one column
    df_cgs_vds_vgs = (
        df_cgs_vds_vgs.set_index([vds_col_name])
        .stack()
        .reset_index(name="cgs")
        .rename(columns={"level_1": "vgs"})
        .rename(columns={vds_col_name: "vds"})
    )

    # Multiplying vgs by -1 for pfet devices to match provided data
    df_cgs_vds_vgs["vds"] = df_cgs_vds_vgs["vds"].apply(lambda x: x * -1) if "pfet" in dev_type else df_cgs_vds_vgs["vds"]

    # Get min/max values of vgs sweep
    vds_min_val = df_cgs_vds_vgs["vds"].min()
    vds_max_val = df_cgs_vds_vgs["vds"].max()

    # Adding columns for all voltage sweeps and output
    df_cgs_vds_vgs["vgs"] = df_cgs_vds_vgs["vgs"].apply(lambda x: x.split("=")[1])
    df_cgs_vds_vgs["vgs"] = df_cgs_vds_vgs["vgs"].astype(float)
    df_cgs_vds_vgs["vbs"] = vbs_df_cgs_vds_vgs
    df_cgs_vds_vgs["const_var"] = "vbs"
    df_cgs_vds_vgs["const_var_val"] = vbs_df_cgs_vds_vgs
    df_cgs_vds_vgs["out_col"] = "cgs"

    # Get vds sweep values
    vgs_min_val = df_cgs_vds_vgs["vgs"].min()
    vgs_max_val = df_cgs_vds_vgs["vgs"].max()
    vgs_step_val = abs(df_cgs_vds_vgs["vgs"][1] - df_cgs_vds_vgs["vgs"][0])

    # Adding sweeps used per each variation
    df_cgs_vds_vgs[
        "sweeps"
    ] = f"vds {vds_min_val} {vds_max_val} {vds_step_val} vgs {vgs_min_val} {vgs_max_val} {vgs_step_val}"

    return df_cgs_vds_vgs


def parse_cgg_vgs_vds(sub_df, dev_type, dev_name):
    """
    Function to parse measurement data for Cgg Vs Vgs with Vds sweep to be used in simulation.

    Parameters
    ----------
    sub_df : pd.DataFrame
        DataFrame that holds sub measurement information per each variation.
    dev_type : str
        Type of device we want to extract data for [nfet or pfet].
    dev_name : str
        Device we want to extract data for.
    Returns
    ----------
    df_cgg_vgs_vds : pd.DataFrame
        DataFrame that holds all measurement points for Cgg Vs Vgs with Vds sweep
    """

    # Get no of cols per variation for vbs sweep
    NUM_COLS_MEAS_VBS = NUM_COLS_MEAS_VBS_03v3 if '03v3' in dev_name else NUM_COLS_MEAS_VBS_06v0

    ## Cgc Vs Vgs [Vbs sweep]
    df_cgg_vgs_vds = sub_df.iloc[
        :, NUM_COLS_MEAS_VBS : NUM_COLS_MEAS_VBS + NUM_COLS_MEAS_VDS_CV
    ]

    vbs_df_cgg_vgs_vds = float(df_cgg_vgs_vds.columns[0].split("/")[0].split("=")[1])
    df_cgg_vgs_vds.drop(columns=df_cgg_vgs_vds.columns[0], inplace=True)

    # Get vgs sweep values
    vgs_col_name = "Vgs (V).1"

    # Get Vgs step value
    vgs_step_val = round(abs(df_cgg_vgs_vds[vgs_col_name][1] - df_cgg_vgs_vds[vgs_col_name][0]), 2)

    # Stacking all vbs sweeps in one column
    df_cgg_vgs_vds = (
        df_cgg_vgs_vds.set_index([vgs_col_name])
        .stack()
        .reset_index(name="cgg")
        .rename(columns={"level_1": "vds"})
        .rename(columns={vgs_col_name: "vgs"})
    )

    # Multiplying vgs by -1 for pfet devices to match provided data
    df_cgg_vgs_vds["vgs"] = df_cgg_vgs_vds["vgs"].apply(lambda x: x * -1) if "pfet" in dev_type else df_cgg_vgs_vds["vgs"]

    # Get min/max values of vgs sweep
    vgs_min_val = df_cgg_vgs_vds["vgs"].min()
    vgs_max_val = df_cgg_vgs_vds["vgs"].max()

    # Adding columns for all voltage sweeps and output
    df_cgg_vgs_vds["vds"] = df_cgg_vgs_vds["vds"].apply(lambda x: x.split("=")[1])
    df_cgg_vgs_vds["vds"] = df_cgg_vgs_vds["vds"].astype(float)
    df_cgg_vgs_vds["vbs"] = vbs_df_cgg_vgs_vds
    df_cgg_vgs_vds["const_var"] = "vds"
    df_cgg_vgs_vds["const_var_val"] = vbs_df_cgg_vgs_vds
    df_cgg_vgs_vds["out_col"] = "cgg"

    # Get vds sweep values
    vbs_min_val = df_cgg_vgs_vds["vds"].min()
    vbs_max_val = df_cgg_vgs_vds["vds"].max()
    vbs_step_val = abs(df_cgg_vgs_vds["vds"][1] - df_cgg_vgs_vds["vds"][0])

    # Adding sweeps used per each variation
    df_cgg_vgs_vds[
        "sweeps"
    ] = f"vgs {vgs_min_val} {vgs_max_val} {vgs_step_val} vbs {vbs_min_val} {vbs_max_val} {vbs_step_val}"

    return df_cgg_vgs_vds


def parse_cgc_vgs_vbs(sub_df, dev_type, dev_name):
    """
    Function to parse measurement data for Cgc Vs Vgs with Vbs sweep to be used in simulation.

    Parameters
    ----------
    sub_df : pd.DataFrame
        DataFrame that holds sub measurement information per each variation.
    dev_type : str
        Type of device we want to extract data for [nfet or pfet].
    dev_name : str
        Device we want to extract data for.
    Returns
    ----------
    df_cgc_vgs_vbs : pd.DataFrame
        DataFrame that holds all measurement points for Cgc Vs Vgs with Vbs sweep
    """

    # Get no of cols per variation for vbs sweep
    NUM_COLS_MEAS_VBS = NUM_COLS_MEAS_VBS_03v3 if '03v3' in dev_name else NUM_COLS_MEAS_VBS_06v0

    ## Cgc Vs Vgs [Vbs sweep]
    df_cgc_vgs_vbs = sub_df.iloc[:, :NUM_COLS_MEAS_VBS]
    vds_df_cgc_vgs_vbs = float(df_cgc_vgs_vbs.columns[0].split("/")[0].split("=")[1])
    df_cgc_vgs_vbs.drop(columns=df_cgc_vgs_vbs.columns[0], inplace=True)

    # Get vgs sweep values
    vgs_col_name = "Vgs (V)"

    # Get Vgs step value
    vgs_step_val = round(abs(df_cgc_vgs_vbs[vgs_col_name][1] - df_cgc_vgs_vbs[vgs_col_name][0]), 2)

    # Stacking all vbs sweeps in one column
    df_cgc_vgs_vbs = (
        df_cgc_vgs_vbs.set_index([vgs_col_name])
        .stack()
        .reset_index(name="cgc")
        .rename(columns={"level_1": "vbs"})
        .rename(columns={vgs_col_name: "vgs"})
    )

    # Multiplying vgs by -1 for pfet devices to match provided data
    df_cgc_vgs_vbs["vgs"] = df_cgc_vgs_vbs["vgs"].apply(lambda x: x * -1) if "pfet" in dev_type else df_cgc_vgs_vbs["vgs"]

    # Get min/max values of vgs sweep
    vgs_min_val = df_cgc_vgs_vbs["vgs"].min()
    vgs_max_val = df_cgc_vgs_vbs["vgs"].max()

    # Adding columns for all voltage sweeps and output
    df_cgc_vgs_vbs["vbs"] = df_cgc_vgs_vbs["vbs"].apply(lambda x: x.split("=")[1])
    df_cgc_vgs_vbs["vbs"] = df_cgc_vgs_vbs["vbs"].astype(float)
    df_cgc_vgs_vbs["vds"] = vds_df_cgc_vgs_vbs
    df_cgc_vgs_vbs["const_var"] = "vds"
    df_cgc_vgs_vbs["const_var_val"] = vds_df_cgc_vgs_vbs
    df_cgc_vgs_vbs["out_col"] = "cgc"

    # Get vgs sweep values
    vbs_min_val = df_cgc_vgs_vbs["vbs"].min()
    vbs_max_val = df_cgc_vgs_vbs["vbs"].max()
    vbs_step_val = abs(df_cgc_vgs_vbs["vbs"][1] - df_cgc_vgs_vbs["vbs"][0])

    # Adding sweeps used per each variation
    df_cgc_vgs_vbs[
        "sweeps"
    ] = f"vgs {vgs_min_val} {vgs_max_val} {vgs_step_val} vbs {vbs_min_val} {vbs_max_val} {vbs_step_val}"

    return df_cgc_vgs_vbs


def parse_fet_cv_sweeps(sub_df, dev_type, dev_name):
    """
    Function to parse measurement data to be used in simulation.

    Parameters
    ----------
    sub_df : pd.DataFrame
        DataFrame that holds sub measurement information per each variation.
    dev_type : str
        Type of device we want to extract data for [nfet or pfet].
    dev_name : str
        Device we want to extract data for.
    Returns
    -------
    df_cv_sweeps : pd.DataFrame
        DataFrame that holds all extracted points for cv measurement
    """

    ## Cgc Vs Vgs [Vbs sweep]
    df_cgc_vgs_vbs = parse_cgc_vgs_vbs(sub_df, dev_type, dev_name)

    ## Cgg Vs Vgs [Vds sweep]
    df_cgg_vgs_vds = parse_cgg_vgs_vds(sub_df, dev_type, dev_name)

    # ## Cgs Vs Vds [Vgs sweep]
    df_cgs_vds_vgs = parse_cgs_vds_vgs(sub_df, dev_type, dev_name)

    # ## Cgd Vs Vds [Vgs sweep]
    df_cgd_vds_vgs = parse_cgd_vds_vgs(sub_df, dev_type, dev_name)

    df_cv_sweeps = pd.concat([df_cgc_vgs_vbs, df_cgg_vgs_vds, df_cgs_vds_vgs, df_cgd_vds_vgs])

    return df_cv_sweeps


def gen_cv_sweeps(all_dfs, dev_name):
    """
    Function to generate full data frame of measured data with all variations.

    Parameters
    ----------
    all_dfs : pd.DataFrame
        DataFrame that holds all the measurement data after extraction.
    dev_name : str
        Device we want to extract data for.
    Returns
    -------
        None
    """

    # Generate csv file contains simulation sweeps
    ## Re-arranging columns of sweep data file
    sweeps_df_cols = [
        "device_name",
        "W (um)",
        "L (um)",
        "nf",
        "corner",
        "temp",
        "const_var",
        "const_var_val",
        "sweeps",
        "out_col",
    ]
    sweeps_df = all_dfs.reindex(columns=sweeps_df_cols)
    sweeps_df.drop_duplicates(inplace=True)

    # Splitting sweeps depends one selected measured output
    sweeps_df_cgc = sweeps_df[sweeps_df['out_col'] == 'cgc']
    sweeps_df_cgg = sweeps_df[sweeps_df['out_col'] == 'cgg']
    sweeps_df_cgs = sweeps_df[sweeps_df['out_col'] == 'cgs']
    sweeps_df_cgd = sweeps_df[sweeps_df['out_col'] == 'cgd']
    # Drop out_col columns as it will be redundant
    sweeps_df_cgc = sweeps_df_cgc.drop('out_col', axis=1)
    sweeps_df_cgg = sweeps_df_cgg.drop('out_col', axis=1)
    sweeps_df_cgs = sweeps_df_cgs.drop('out_col', axis=1)
    sweeps_df_cgd = sweeps_df_cgd.drop('out_col', axis=1)
    # Saving sweep data files to csv
    sweeps_df_cgc.to_csv(f"{dev_name}_sweeps_cgc.csv", index=False)
    sweeps_df_cgg.to_csv(f"{dev_name}_sweeps_cgg.csv", index=False)
    sweeps_df_cgs.to_csv(f"{dev_name}_sweeps_cgs.csv", index=False)
    sweeps_df_cgd.to_csv(f"{dev_name}_sweeps_cgd.csv", index=False)
    # logs for info
    logging.info(f"Number of sweep points for {dev_name}-cgc: {len(sweeps_df_cgc)}")
    logging.info(f"Number of sweep points for {dev_name}-cgc: {len(sweeps_df_cgg)}")
    logging.info(f"Number of sweep points for {dev_name}-cgc: {len(sweeps_df_cgs)}")
    logging.info(f"Number of sweep points for {dev_name}-cgc: {len(sweeps_df_cgd)}")
    logging.info(f"Sweep csv file for {dev_name}-cgc at : {dev_name}_sweeps_cgc.csv")
    logging.info(f"Sweep csv file for {dev_name}-cgg at : {dev_name}_sweeps_cgg.csv")
    logging.info(f"Sweep csv file for {dev_name}-cgs at : {dev_name}_sweeps_cgs.csv")
    logging.info(f"Sweep csv file for {dev_name}-cgd at : {dev_name}_sweeps_cgd.csv")


def gen_cv_variations(df, dp_df, dev_name, variations_count):
    """
    Function to generate full data frame of measured data with all variations.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame that holds all the measurement information for selected fet.
    dp_df : pd.DataFrame
        DataFrame that holds all data points for all varaitions.
    dev_name : str
        Device we want to extract data for.
    variations_count : float
        Number of variations per each selected device
    Returns
    -------
        None
    """

    # Get number of columns that holds measurement data for each variation
    # Get columns names that holds data for each variation
    num_data_col_per_dp, orig_col_names = get_orig_col_names(df, variations_count)

    # Generating all data points per each variation and combining all data in one DF
    all_dfs = []
    no_cols_df = len(df.columns)
    for i in range(0, no_cols_df, num_data_col_per_dp):
        # Half data for nfet and other half for pfet
        dev_type = 'nfet' if i < no_cols_df / 2 else 'pfet'
        # Get sub dataframe per each sweep
        sub_df = df[df.columns[i : i + num_data_col_per_dp]].copy()
        sub_df.columns = orig_col_names
        parsed_df = parse_fet_cv_sweeps(sub_df, dev_type, dev_name)
        for c in dp_df.columns:
            parsed_df[c] = dp_df.loc[len(all_dfs), c]
        all_dfs.append(parsed_df)

    all_dfs = pd.concat(all_dfs)
    all_dfs.drop_duplicates(inplace=True)

    # Generate data file that holds all sweep values per each variation to be used in simulation
    gen_cv_sweeps(all_dfs, dev_name)

    # Generate final data file that holds all data points to be used in comparision
    ## Re-arranging columns of final data file
    all_dfs_cols = [
        "device_name",
        "W (um)",
        "L (um)",
        "nf",
        "corner",
        "temp",
        "vds",
        "vgs",
        "vbs",
        "cgc",
        "cgg",
        "cgs",
        "cgd",
    ]
    all_dfs = all_dfs.reindex(columns=all_dfs_cols)

    logging.info(f"Length of all data points {len(all_dfs)}")

    return all_dfs


def fet_cv_meas_extraction(df: pd.DataFrame, dev_name: str):
    """
    Function to extract measurement data for Fets-CV.

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
    cgc_cols = [c for c in df.columns if "Cgc (fF)" in c]
    cgg_cols = [c for c in df.columns if "Cgg (fF)" in c]
    cgs_cols = [c for c in df.columns if "Cgs (fF)" in c]
    cgd_cols = [c for c in df.columns if "Cgd (fF)" in c]

    unwanted_cols = ["CV"] + cgc_cols + cgg_cols + cgs_cols + cgd_cols

    # Cleanup dataframe from unwanted columns we don't use
    df = dataframe_cleanup(df, unwanted_cols)

    # Get num of variations for fets depending on length values in data
    variations_count = get_variation_count(df, "L (um)")

    # For MOS-CV 03v3/06v0, There are 8 variations = 4*2 [For device_type * W_L_variation * corners * temp]
    ## We have 2 types of MOS-CV [nfet, pfet]
    ## We have 4 W&L combination [(200, 0.28), (100, 10), (0.22, 0.28), (0.22, 10) um]
    ## We have 1 corners [typical]
    ## We have 1 temperature [25]

    all_temp = (
        [25] * variations_count
    )

    # Define new data frame that holds all variations
    dp_df = pd.DataFrame({'temp': all_temp})

    # "Unnamed: 2" cols: This column holds some info related to each device [name, W&L&nf]
    ## Example nmos_3p3 (200u x0.28u ,  nf=20,  m=1)
    dp_df["device_data"] = df["Unnamed: 2"].copy()
    dp_df["device_name"] = dp_df["device_data"].apply(lambda x: x.split("\n")[0])
    dp_df["W (um)"] = dp_df["device_data"].apply(lambda x: x.split("\n")[1].split("x")[0].replace("(", "").replace("u", ""))
    dp_df["L (um)"] = dp_df["device_data"].apply(lambda x: x.split("\n")[1].split("x")[1].split(",")[0].replace("u", ""))
    dp_df["nf"] = dp_df["device_data"].apply(lambda x: x.split("=")[1].split(",")[0])
    dp_df["W (um)"] = dp_df["W (um)"].astype(float)
    dp_df["L (um)"] = dp_df["L (um)"].astype(float)
    dp_df["nf"] = dp_df["nf"].astype(int)
    dp_df["corner"] = df["corners"].copy()
    dp_df.drop('device_data', axis=1, inplace=True)

    # Updating devices names to match latest names for GF180MCU models
    dp_df["device_name"] = dp_df["device_name"].apply(lambda x: x.replace("nmos", "nfet").replace("3p3", "03v3"))
    dp_df["device_name"] = dp_df["device_name"].apply(lambda x: x.replace("pmos", "pfet").replace("6p0", "06v0"))
    dp_df["device_name"] = dp_df["device_name"].apply(lambda x: x.replace("sab", "dss").replace("nat", "nvt"))

    # Cleanup dataframe from unwanted columns we don't use
    unwanted_cols = ["W (um)", "L (um)", 'Unnamed: 2', 'corners']
    df = dataframe_cleanup(df, unwanted_cols)

    # Generate the full dataframe that holds all meas data in a clean format
    all_dfs = gen_cv_variations(df, dp_df, dev_name, variations_count)

    # Writing final dataframe that holds all clean data
    all_dfs.drop_duplicates(inplace=True)

    # Splitting final df depends on measured output
    all_dfs_cgc = all_dfs.loc[all_dfs['cgc'].notnull()]
    all_dfs_cgg = all_dfs.loc[all_dfs['cgg'].notnull()]
    all_dfs_cgs = all_dfs.loc[all_dfs['cgs'].notnull()]
    all_dfs_cgd = all_dfs.loc[all_dfs['cgd'].notnull()]

    # Drop some unwanted columns as it will be redundant
    all_dfs_cgc = all_dfs_cgc.drop(['cgg', 'cgs', 'cgd'], axis=1)
    all_dfs_cgg = all_dfs_cgg.drop(['cgc', 'cgs', 'cgd'], axis=1)
    all_dfs_cgs = all_dfs_cgs.drop(['cgc', 'cgg', 'cgd'], axis=1)
    all_dfs_cgd = all_dfs_cgd.drop(['cgc', 'cgg', 'cgs'], axis=1)

    # Saving full extracted measured data to csv
    all_dfs_cgc.to_csv(f"{dev_name}_meas_cgc.csv", index=False)
    all_dfs_cgg.to_csv(f"{dev_name}_meas_cgg.csv", index=False)
    all_dfs_cgs.to_csv(f"{dev_name}_meas_cgs.csv", index=False)
    all_dfs_cgd.to_csv(f"{dev_name}_meas_cgd.csv", index=False)

    # logs for info
    logging.info(
        f"Full extracted measurement data for {dev_name}-cgc at: {dev_name}_meas_cgc.csv"
    )
    logging.info(
        f"Full extracted measurement data for {dev_name}-cgg at: {dev_name}_meas_cgg.csv"
    )
    logging.info(
        f"Full extracted measurement data for {dev_name}-cgs at: {dev_name}_meas_cgs.csv"
    )
    logging.info(
        f"Full extracted measurement data for {dev_name}-cgd at: {dev_name}_meas_cgd.csv"
    )
