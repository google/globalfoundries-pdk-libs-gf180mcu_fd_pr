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

# CONSTANT VALUES
## These values are manually selected after some analysis
## for provided measuremnet data.
# === RES ===
DEFAULT_TEMP = 25.0
DEFAULT_VOLTAGE = 1.0


def ext_const_temp_corners(df: pd.DataFrame, dev_name: str) -> pd.DataFrame:
    """
    Function to extract measurement data for RES-R measurement with W&L variations.

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

    # Process corners measured in RES-R
    corners = ["typical", "ff", "ss"]

    all_dfs = []
    for corner in corners:
        idf = df[["l (um)", "w (um)", f"res_{corner} Rev9 "]].copy()
        idf.rename(
            columns={
                f"res_{corner} Rev9 ": "res",
                "l (um)": "length",
                "w (um)": "width",
            },
            inplace=True,
        )
        idf["corner"] = corner
        all_dfs.append(idf)

    df = pd.concat(all_dfs)
    df["temp"] = DEFAULT_TEMP
    df["device"] = dev_name
    df["voltage"] = DEFAULT_VOLTAGE
    df.dropna(axis=0, inplace=True)
    df = df[["device", "corner", "length", "width", "voltage", "temp", "res"]]

    # Writing final dataframe that holds all clean data
    df.drop_duplicates(inplace=True)
    df.to_csv(f"{dev_name}_res_wl_meas.csv", index=False)
    logging.info(f"Full extracted measurement data for {dev_name}-r with W&L variation:\n {df}")
    logging.info(
        f"Full extracted measurement data for {dev_name}-r with W&L variation at: {dev_name}_res_wl_meas.csv"
    )


def ext_temp_corners(df: pd.DataFrame, dev_name: str) -> pd.DataFrame:
    """
    Function to extract measurement data for RES-R measurement with temp variations.

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

    # Process corners measured in RES-R
    corners = ["typical", "ff", "ss"]

    all_dfs = []
    for corner in corners:
        idf = df[
            ["Temperature (C)", "l (um)", "Unnamed: 2", f"res_{corner} Rev9 "]
        ].copy()
        idf.rename(
            columns={
                f"res_{corner} Rev9 ": "res",
                "l (um)": "length",
                "Unnamed: 2": "info",
                "Temperature (C)": "temp",
            },
            inplace=True,
        )
        idf["corner"] = corner
        all_dfs.append(idf)

    df = pd.concat(all_dfs)
    df["width"] = df["info"].str.extract(r"w=([\d\.]+)").astype(float)
    df["device"] = dev_name
    df["voltage"] = DEFAULT_VOLTAGE
    df.dropna(axis=0, inplace=True)
    df = df[["device", "corner", "length", "width", "voltage", "temp", "res"]]

    # Writing final dataframe that holds all clean data
    df.drop_duplicates(inplace=True)
    df.to_csv(f"{dev_name}_res_temp_meas.csv", index=False)
    logging.info(f"Full extracted measurement data for {dev_name}-r with temp variation:\n {df}")
    logging.info(
        f"Full extracted measurement data for {dev_name}-r with temp variation at: {dev_name}_res_temp_meas.csv"
    )
