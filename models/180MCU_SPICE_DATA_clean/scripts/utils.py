
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

import logging


def dataframe_cleanup(df, unwanted_cols):
    """
    Function to clean data frame from unwanted cols.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame we want to clean it
    unwanted_cols: list
        List of unwanted columns you need to remove
    Returns
    -------
    df : pd.DataFrame
        Output dataFrame after removing unwanted cols.
    """

    # Get the columns with only NaN values
    nan_columns = df.columns[df.isna().all()]
    # Drop the columns with only NaN values
    df.drop(columns=nan_columns, inplace=True)
    df.drop(columns=unwanted_cols, inplace=True)

    return df


def stack_df_cols(sub_df, col_untouched, stacked_col_name, stacked_col_index):
    """
    Function to stack dataframe columns in new column with column index.

    Parameters
    ----------
    sub_df : pd.DataFrame
        DataFrame that we need to stack columns in it.
    col_untouched : str
       Name of column that we need to keep it untouched while stacking other columns.
    stacked_col_name : str
       Name of column we stack all data of other columns in it.
    stacked_col_index : str
        Name of column that contains index of stacked columns.
    Returns
    -------
        stack_df_cols: Reshaped dataframe that contains stacked columns with column index.
    """

    sub_df = (
        sub_df.set_index([col_untouched])
        .stack()
        .reset_index(name=stacked_col_index)
        .rename(columns={"level_1": stacked_col_name})
    )

    return sub_df


def get_variation_count(df, col_name):
    """
    Function to extract measurement data for Fets.

    Parameters
    ----------
    df : pd.dataframe
        Data frame for measured data to get variaitons from it
    col_name : str
        Name of column we will use to count it as a variation.
    Returns
    -------
        variation_count: Number of variations in the provided dataframe
    """
    # Get num of variations for fets depending on length values in data
    variations_count = df[col_name].count()

    logging.info(f"No of variations are {variations_count}")
    logging.info(f"Length of data points is {len(df.columns)}")

    return variations_count


def get_orig_col_names(df, variations_count):
    """
    Function to get original columns names for dataframe and number of columns per variation.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame we need to extract some info from it
    variations_count: int
        Number of variation in the dataframe
    Returns
    -------
        num_data_col_per_dp: Number of data columns per variation
        orig_col_names: Original column names of dataframe per variation
    """

    # Get number of columns that holds measurement data for each variation
    num_data_col_per_dp = int(len(df.columns) / variations_count)
    # Get columns names that holds data for each variation
    orig_col_names = df.columns[:num_data_col_per_dp]

    logging.info(f" No of data columns per variation: {num_data_col_per_dp}")
    logging.info(f" Original columns per variation:\n {orig_col_names}")

    return num_data_col_per_dp, orig_col_names
