# Copyright 2022 GlobalFoundries PDK Authors
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
Run GlobalFoundries 180nm BCDLite DRC Unit Regression.

Usage:
    run_regression.py (--help| -h)
    run_regression.py [--mp=<num>] [--run_name=<run_name>] [--rule_name=<rule_name>] [--table_name=<table_name>]

Options:
    --help -h                           Print this help message.
    --mp=<num>                          The number of threads used in run.
    --run_name=<run_name>               Select your run name.
    --rule_name=<rule_name>             Target specific rule.
    --table_name=<table_name>           Target specific table.
"""

from subprocess import check_call
from subprocess import Popen, PIPE
import concurrent.futures
import traceback
import yaml
import shutil
from docopt import docopt
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import time
import pandas as pd
import logging
import glob
from pathlib import Path
from tqdm import tqdm
import re 


SUPPORTED_TC_EXT = "gds"
SUPPORTED_SW_EXT = "yaml"

def check_klayout_version():
    """
    check_klayout_version checks klayout version and makes sure it would work with the DRC.
    """
    # ======= Checking Klayout version =======
    klayout_v_ = os.popen("klayout -b -v").read()
    klayout_v_ = klayout_v_.split("\n")[0]
    klayout_v_list = []

    if klayout_v_ == "":
        logging.error("Klayout is not found. Please make sure klayout is installed.")
        exit(1)
    else:
        klayout_v_list = [int(v) for v in klayout_v_.split(" ")[-1].split(".")]

    logging.info(f"Your Klayout version is: {klayout_v_}")

    if len(klayout_v_list) < 1 or len(klayout_v_list) > 3:
        logging.error("Was not able to get klayout version properly.")
        exit(1)
    elif len(klayout_v_list) == 2:
        if klayout_v_list[1] < 28:
            logging.warning(f"Prerequisites at a minimum: KLayout 0.28.0")
            logging.error(
                "Using this klayout version has not been assesed in this development. Limits are unknown"
            )
            exit(1)
    elif len(klayout_v_list) == 3:
        if klayout_v_list[1] < 28 :
            logging.warning(f"Prerequisites at a minimum: KLayout 0.28.0")
            logging.error(
                "Using this klayout version has not been assesed in this development. Limits are unknown"
            )
            exit(1)

def get_switches(yaml_file,rule_name):
    """Parse yaml file and extract switches data
    Parameters
    ----------
    yaml_file : str
            yaml config file path given py the user.
    Returns
    -------
    yaml_dic : dictionary
            dictionary containing switches data.
    """

    # load yaml config data
    with open(yaml_file, 'r') as stream:
        try:
            yaml_dic = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    switches = list()
    for param,value in yaml_dic[rule_name].items():
        switch = f"{param}={value}"
        switches.append(switch)

    return switches



def generate_merged_gds(rule_deck_path , testcase_path , db_path ):
    # Get the same rule deck with gds output
    
    # Marker layers
    ly_num = 10000
    ly_dt = 0
    
    # Generation of merged gds 
    # GDS file contains violations markers merged
    #  with original testcases
    num_exc = 0
    merged_gds_source = f'\n source.layout.write("merged_output.gds") \n'
    with open(rule_deck_path, 'r') as lines:
        with open("markers.drc", 'w') as marker:
            for num,line in enumerate(lines):
                if ".output" in line:
                    line = re.sub(r'\([\s\S]*\)', f'({ly_num}, {ly_dt})', line )
                    ly_dt +=1
                
                if "if $report" in line:
                    num_exc = num

                if num not in range(num_exc,num_exc+7):
                    marker.write(line)                
            marker.write(merged_gds_source)                

    call_str = f"klayout -b -r markers.drc -rd input={testcase_path} -rd report={db_path}"    
    check_call(call_str, shell=True)

def parse_results_db(results_database):
    """
    This function will parse Klayout database for analysis.

    Parameters
    ----------
    results_database : string or Path object
        Path string to the results file
    
    Returns
    -------
    set
        A set that contains all rules in the database with violations
    """

    mytree = ET.parse(results_database)
    myroot = mytree.getroot()

    all_violating_rules = set()

    for z in myroot[7]:  # myroot[7] : List rules with viloations
        all_violating_rules.add(f"{z[1].text}".replace("'", ""))

    return all_violating_rules


def run_test_case(
    runset_file,
    drc_dir,
    layout_path,
    run_dir,
    test_table,
    test_rule,
    switches="",
):
    """
    This function run a single test case using the correct DRC file.

    Parameters
    ----------
    runset_file : string or None
        Filename of the runset to be used.
    drc_dir : string or Path
        Path to the location where all runsets exist.
    layout_path : stirng or Path object
        Path string to the layout of the test pattern we want to test.
    run_dir : stirng or Path object
        Path to the location where is the regression run is done.
    switches : string
        String that holds all the DRC run switches required to enable this.
    
    Returns
    -------
    pd.DataFrame
        A pandas DataFrame with the rule and rule deck used.
    """

    # Get switches used for each run
    sw_file = os.path.join(Path(layout_path.parent.parent).absolute(), f"{test_rule}.{SUPPORTED_SW_EXT}")

    if os.path.exists(sw_file):
        switches = " ".join(get_switches(sw_file, test_rule))        
    else:
        switches = "--variant=C"  # default switch

    pattern_clean = ".".join(os.path.basename(layout_path).split(".")[:-1])
    output_loc = f"{run_dir}/{test_table}/{test_rule}_patterns"
    pattern_log = f"{output_loc}/{pattern_clean}_drc.log"
    
    os.makedirs(output_loc, exist_ok=True)

    if "antenna" in runset_file:
        switches += " --antenna_only"
    elif "density" in runset_file:
        switches += " --density_only"

    call_str = f"python3 {drc_dir}/run_drc.py --path={layout_path} {switches} --table={test_table} --run_dir={output_loc} --run_mode=flat --thr=1  > {pattern_log} 2>&1"
    try:
        check_call(call_str, shell=True)
    except Exception as e:
        pattern_results = glob.glob(os.path.join(output_loc, f"{pattern_clean}*.lyrdb"))
        if len(pattern_results) < 1:
            logging.error("%s generated an exception: %s" % (pattern_clean, e))
            traceback.print_exc()
            raise
    
    pattern_results = glob.glob(os.path.join(output_loc, f"{pattern_clean}*.lyrdb"))
    if len(pattern_results) > 0:
        violated_rules = set()
        for p in pattern_results:
            rules_with_violations = parse_results_db(p)
            violated_rules.update(rules_with_violations)

        if test_rule in violated_rules:
            return "false_negative"
        else:
            return "true_positive"

        # if test_rule in violated_rules:
        #     return "true_negative"
        # else:
        #     return "false_positive"
    else:
        return "database_not_found"


def run_all_test_cases(tc_df, run_dir, thrCount):
    """
    This function run all test cases from the input dataframe.

    Parameters
    ----------
    tc_df : pd.DataFrame
        DataFrame that holds all the test cases information for running.
    run_dir : string or Path
        Path string to the location of the testing code and output.
    thrCount : int
        Numbe of threads to use per klayout run.
    
    Returns
    -------
    pd.DataFrame
        A pandas DataFrame with all test cases information post running.
    """

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_run_id = dict()
        for i, row in tc_df.iterrows():
            future_to_run_id[
                executor.submit(
                    run_test_case,
                    str(row["runset"]),
                    drc_dir,
                    row["test_path"],
                    run_dir,
                    row["table_name"],
                    row["rule_name"],
                    thrCount,
                )
            ] = row["run_id"]

        for future in concurrent.futures.as_completed(future_to_run_id):
            run_id = future_to_run_id[future]
            try:
                status_string = future.result()
            except Exception as exc:
                logging.error("%d generated an exception: %s" % (run_id, exc))
                traceback.print_exc()
                status_string = "exception"

            info = dict()
            info["run_id"] = run_id
            info["run_status"] = status_string
            results.append(info)

    results_df = pd.DataFrame(results)
    all_runs_df = tc_df.merge(results_df, on="run_id", how="left")

    return all_runs_df


def parse_existing_rules(rule_deck_path, output_path):
    """
    This function collects the rule names from the existing drc rule decks.

    Parameters
    ----------
    rule_deck_path : string or Path object
        Path string to the DRC directory where all the DRC files are located.
    output_path : string or Path
        Path of the run location to store the output analysis file.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame with the rule and rule deck used.
    """

    drc_files = glob.glob(os.path.join(rule_deck_path, "rule_decks", "*.drc"))
    rules_data = list()

    for runset in drc_files:
        with open(runset, "r") as f:
            for line in f:
                if ".output" in line:
                    line_list = line.split('"')
                    rule_info = dict()
                    rule_info["runset"] = os.path.basename(runset)
                    rule_info["rule_name"] = line_list[1]
                    rules_data.append(rule_info)

    df = pd.DataFrame(rules_data)
    df.drop_duplicates(inplace=True)
    df.to_csv(os.path.join(output_path, "rule_deck_rules.csv"), index=False)
    return df


def analyze_test_patterns_coverage(rules_df, tc_df, output_path):
    """
    This function analyze the test patterns before running the test cases.

    Parameters
    ----------
    rules_df : pd.DataFrame
        DataFrame that holds all the rules that are found in the rule deck.
    tc_df : pd.DataFrame
        DataFrame that holds all the test cases and all the information required.
    output_path : string or Path
        Path of the run location to store the output analysis file.

    Returns
    -------
    pd.DataFrame
        A DataFrame with analysis of the rule testing coverage.
    """
    cov_df = (
        tc_df[["table_name", "rule_name"]]
        .groupby(["table_name", "rule_name"])
        .count()
        .reset_index(drop=False)
    )
    cov_df = cov_df.merge(rules_df, on="rule_name", how="outer")
    cov_df["runset"].fillna("", inplace=True)
    cov_df.to_csv(os.path.join(output_path, "testcases_coverage.csv"), index=False)

    return cov_df


def analyze_regression_run(tc_cv_df, all_tc_df, output_path):
    """
    This function analyze the regression run post running and generate a report with all the required details.

    Parameters
    ----------
    tc_cv_df : pd.DataFrame
        DataFrame that holds the test cases cover report.
    all_tc_df : pd.DataFrame
        DataFrame that holds all the test cases and the run results associated.
    output_path : string or Path
        Path of the run location to store the output analysis file.

    Returns
    -------
    pd.DataFrame
        A DataFrame with analysis of the rule testing coverage.
    """
    cov_rows_df = (
        all_tc_df[["table_name", "rule_name", "test_type", "test_name", "run_status"]]
        .groupby(["table_name", "rule_name", "test_type", "run_status"])
        .count()
        .reset_index(drop=False)
        .rename(columns={"test_name": "count"})
    )

    cov_df = cov_rows_df.pivot(
        index=["table_name", "rule_name"],
        columns=["test_type", "run_status"],
        values=["count"],
    ).reset_index(drop=False)
    cov_df.columns = ["_".join(pair) for pair in cov_df.columns]
    cov_df.rename(
        columns={"table_name__": "table_name", "rule_name__": "rule_name"}, inplace=True
    )

    cov_df = cov_df.merge(tc_cv_df, on=["rule_name", "table_name"], how="outer")
    all_count_columns = [c for c in cov_df.columns if "count" in c]

    cov_df[all_count_columns] = cov_df[all_count_columns].fillna(0).astype(int)

    cov_df["runset"].fillna("", inplace=True)
    cov_df.to_csv(os.path.join(output_path, "regression_run_analysis.csv"), index=False)

    return cov_df


def convert_results_db_to_gds():
    pass


def get_unit_tests_dataframe(gds_files):
    """
    This function is used for getting all test cases available in a formated data frame before running.

    Parameters
    ----------
    gds_files : str
        Path string to the location of unit test cases path.
    Returns
    -------
    pd.DataFrame
        A DataFrame that has all the targetted test cases that we need to run.
    """

    # Get rules from gds
    rules = []
    tc_df = pd.DataFrame()

    for gds_file in gds_files:
        with open('gen.rb', 'w') as f:
            f.write(
                f''' 
                layout = RBA::Layout::new
                layout.read("{gds_file}")
                layer_info = "11/222"
                layout.layer_indices.each do |layer_id|
                    layout.each_cell do |cell|
                        if cell.name.include? "RuleName_"
                            cell.each_shape(layer_id) do |shape|
                                if shape.to_s.include? "text"
                                    puts layer_info.to_s
                                    puts shape.to_s
                                end
                            end
                        end
                    end
                end
                ''')
        results = Popen(['klayout', '-b', '-r' ,'gen.rb' , '-rd' , f'input={gds_file}' ], stdout=PIPE, stderr=PIPE)
        stdout, stderr = results.communicate()
        rules = str(stdout).split("'")[1::2]
        rules.sort()

        for rule in rules:
            tc_df = pd.concat([tc_df, pd.DataFrame.from_records([{'test_path': gds_file, "rule_name": rule}])])
    tc_df["table_name"] = tc_df["rule_name"].apply(
        lambda x: x.split(".")[0]
    )
    os.remove('gen.rb') 

    return tc_df


def build_unit_tests_dataframe(unit_test_cases_dir, target_table, target_rule):
    """
    This function is used for getting all test cases available in a formated data frame before running.

    Parameters
    ----------
    unit_test_cases_dir : str
        Path string to the location of unit test cases path.
    target_table : str or None
        Name of table that we want to run regression for. If None, run all found.
    target_rule : str or None
        Name of rule that we want to run regression for. If None, run all found.

    Returns
    -------
    pd.DataFrame
        A DataFrame that has all the targetted test cases that we need to run.
    """
    all_unit_test_cases = sorted(
        Path(unit_test_cases_dir).rglob("*.{}".format(SUPPORTED_TC_EXT))
    )
    logging.info(
        "## Total number of test cases found: {}".format(len(all_unit_test_cases))
    )

    # Get test cases df from test cases
    tc_df = get_unit_tests_dataframe(all_unit_test_cases)

    ## Filter test cases based on filter provided
    if not target_rule is None:
        tc_df = tc_df[tc_df["rule_name"] == target_rule]

    if not target_table is None:
        tc_df = tc_df[tc_df["table_name"] == target_table]

    if len(tc_df) < 1:
        logging.error("No test cases remaining after filtering.")
        exit(1)

    return tc_df


def run_regression(drc_dir, output_path, target_table, target_rule, cpu_count):
    """
    Running Regression Procedure.

    This function runs the full regression on all test cases.

    Parameters
    ----------
    drc_dir : string
        Path string to the DRC directory where all the DRC files are located.
    output_path : str
        Path string to the location of the output results of the run.
    target_table : string or None
        Name of table that we want to run regression for. If None, run all found.
    target_rule : string or None
        Name of rule that we want to run regression for. If None, run all found.
    cpu_count : int
        Number of cpus to use in running testcases.
    Returns
    -------
    bool
        If all regression passed, it returns true. If any of the rules failed it returns false.
    """
    
    ## Parse Existing Rules
    rules_df = parse_existing_rules(drc_dir, output_path)
    logging.info("## Total number of rules found in rule decks: {}".format(len(rules_df)))
    print(rules_df)

    ## Get all test cases available in the repo.
    test_cases_path = os.path.join(drc_dir, "testing/testcases")
    unit_test_cases_path = os.path.join(test_cases_path, "unit_testcases")
    tc_df = build_unit_tests_dataframe(unit_test_cases_path, target_table, target_rule)
    logging.info("## Total number of rules found in test cases: {}".format(len(tc_df)))

    ## Get tc_df with the correct rule deck per rule.
    tc_df = tc_df.merge(rules_df, how="left", on="rule_name")
    tc_df["run_id"] = tc_df.groupby(['test_path']).ngroup()
    print(tc_df)

    tc_df.to_csv(os.path.join(output_path, "all_test_cases.csv"), index=False)

    ## Do some test cases coverage analysis
    cov_df = analyze_test_patterns_coverage(rules_df, tc_df, output_path)
    print(cov_df)

    exit ()

    ## Run all test cases
    all_tc_df = run_all_test_cases(tc_df, output_path, cpu_count)
    print(all_tc_df)
    all_tc_df.to_csv(
        os.path.join(output_path, "all_test_cases_results.csv"), index=False
    )

    
    ## Analyze regression run and generate a report
    regr_df = analyze_regression_run(cov_df, all_tc_df, output_path)
    print(regr_df)

    ## Check if there any rules that generated false positive or false negative
    failing_results = all_tc_df[
        ~all_tc_df["run_status"].isin(["true_positive", "true_negative"])
    ]
    print(failing_results)
    logging.info("## Failing testcases : {}".format(len(failing_results)))

    if len(failing_results) > 0:
        logging.error("## Some test cases failed .....")
        return False
    else:
        logging.info("## All testcases passed.")
        return True

def main(drc_dir: str, rules_dir: str, output_path: str, target_table: str, target_rule: str):
    """
    Main Procedure.

    This function is the main execution procedure

    Parameters
    ----------
    drc_dir : str
        Path string to the DRC directory where all the DRC files are located.
    rules_dir : str
        Path string to the location of all rule deck files for that variant.
    output_path : str
        Path string to the location of the output results of the run.
    target_table : str or None
        Name of table that we want to run regression for. If None, run all found.
    target_rule : str or None
        Name of rule that we want to run regression for. If None, run all found.
    Returns
    -------
    bool
        If all regression passed, it returns true. If any of the rules failed it returns false.
    """

    # No. of threads
    cpu_count = os.cpu_count() if args["--mp"] == None else int(args["--mp"])
    
    # Pandas printing setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    # info logs for args
    logging.info("## Run folder is: {}".format(run_name))
    logging.info("## Target Table is: {}".format(target_table))
    logging.info("## Target rule is: {}".format(target_rule))

    # Start of execution time
    t0 = time.time()
    
    ## Check Klayout version
    check_klayout_version()

    # Calling regression function
    run_status = run_regression(
        drc_dir, output_path, target_table, target_rule, cpu_count
    )


    #  End of execution time
    logging.info("Total execution time {}s".format(time.time() - t0))

    if run_status:
        logging.info("Test completed successfully.")
    else:
        logging.error("Test failed.")
        exit(1)

# ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================

if __name__ == "__main__":

    # docopt reader
    args = docopt(__doc__, version="DRC Regression: 0.2")
    
    # arguments
    run_name = args["--run_name"]
    target_table = args["--table_name"]
    target_rule = args["--rule_name"]

    if run_name is None:
        # logs format
        run_name = datetime.utcnow().strftime("unit_tests_%Y_%m_%d_%H_%M_%S")

    # Paths of regression dirs
    testing_dir = os.path.dirname(os.path.abspath(__file__))
    drc_dir = os.path.dirname(testing_dir)
    rules_dir = os.path.join(drc_dir, "rule_decks")
    output_path = os.path.join(testing_dir, run_name)

    # Creating output dir
    os.makedirs(output_path, exist_ok=True)

    # logs format
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
        logging.FileHandler(os.path.join(output_path, "{}.log".format(run_name))),
        logging.StreamHandler()
        ],
        format=f"%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )
    
    # Calling main function
    run_status = main(
        drc_dir, rules_dir, output_path, target_table, target_rule
    )
