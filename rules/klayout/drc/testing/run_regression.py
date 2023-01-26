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
Run GlobalFoundries 180nm MCU DRC Unit Regression.

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
import gdstk


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
            logging.warning("Prerequisites at a minimum: KLayout 0.28.0")
            logging.error(
                "Using this klayout version has not been assesed in this development. Limits are unknown"
            )
            exit(1)
    elif len(klayout_v_list) == 3:
        if klayout_v_list[1] < 28 :
            logging.warning("Prerequisites at a minimum: KLayout 0.28.0")
            logging.error(
                "Using this klayout version has not been assesed in this development. Limits are unknown"
            )
            exit(1)


def get_switches(yaml_file, rule_name):
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
    for param, value in yaml_dic[rule_name].items():
        switch = f"{param}={value}"
        switches.append(switch)

    return switches


def parse_results_db(test_rule, results_database):
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
    # Initial values for counter
    pass_patterns = 0
    fail_patterns = 0
    falsePos = 0
    falseNeg = 0

    for z in myroot[7]:
        if f"'{test_rule}_pass_patterns'" == f"{z[1].text}":
            pass_patterns += 1
        if f"'{test_rule}_fail_patterns'" == f"{z[1].text}":
            fail_patterns += 1
        if f"'{test_rule}_false_positive'" == f"{z[1].text}":
            falsePos += 1
        if f"'{test_rule}_false_negative'" == f"{z[1].text}":
            falseNeg += 1

    return pass_patterns, fail_patterns, falsePos, falseNeg


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

    # Initial value for counters
    falsePos_count = 0
    falseNeg_count = 0
    pass_patterns_count = 0
    fail_patterns_count = 0

    # Get switches used for each run
    sw_file = os.path.join(Path(layout_path.parent.parent).absolute(), f"{test_rule}.{SUPPORTED_SW_EXT}")

    if os.path.exists(sw_file):
        switches = " ".join(get_switches(sw_file, test_rule))
    else:
        switches = "--variant=C"  # default switch

    # Adding switches for specific runsets
    if "antenna" in runset_file:
        switches += " --antenna_only"
    elif "density" in runset_file:
        switches += " --density_only"

    # Creating run folder structure
    pattern_clean = ".".join(os.path.basename(layout_path).split(".")[:-1])
    output_loc = f"{run_dir}/{test_table}/{test_rule}_data"
    pattern_log = f"{output_loc}/{pattern_clean}_drc.log"

    # command to run drc
    call_str = f"python3 {drc_dir}/run_drc.py --path={layout_path} {switches} --table={test_table} --run_dir={output_loc} --run_mode=flat --thr=1  > {pattern_log} 2>&1"

    # Starting klayout run
    os.makedirs(output_loc, exist_ok=True)
    try:
        check_call(call_str, shell=True)
    except Exception as e:
        pattern_results = glob.glob(os.path.join(output_loc, f"{pattern_clean}*.lyrdb"))
        if len(pattern_results) < 1:
            logging.error("%s generated an exception: %s" % (pattern_clean, e))
            traceback.print_exc()
            raise

    # Checking if run is completed or failed
    pattern_results = glob.glob(os.path.join(output_loc, f"{pattern_clean}*.lyrdb"))

    if len(pattern_results) > 0:
        # db to gds conversion
        marker_output, runset_analysis = convert_results_db_to_gds(pattern_results[0])

        # Generating merged testcase for violated rules
        merged_output = generate_merged_testcase(layout_path, marker_output)

        # Generating final db file
        if os.path.exists(merged_output):
            final_report = f'{merged_output.split(".")[0]}_final.lyrdb'
            call_str = f"klayout -b -r {runset_analysis} -rd input={merged_output} -rd report={final_report}"
            check_call(call_str, shell=True)

            if os.path.exists(final_report):
                pass_patterns_count, fail_patterns_count, falsePos_count, falseNeg_count = parse_results_db(test_rule, final_report)

                return pass_patterns_count, fail_patterns_count, falsePos_count, falseNeg_count
            else:

                return pass_patterns_count, fail_patterns_count, falsePos_count, falseNeg_count
        else:

            return pass_patterns_count, fail_patterns_count, falsePos_count, falseNeg_count

    else:
        return pass_patterns_count, fail_patterns_count, falsePos_count, falseNeg_count


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

    with concurrent.futures.ThreadPoolExecutor(max_workers=thrCount) as executor:
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
                pass_patterns, fail_patterns, false_positive, false_negative = future.result()
                if pass_patterns + fail_patterns > 0:
                    if false_positive + false_negative == 0:
                        status_string = "Passed_rule"
                    else:
                        status_string = "Failed_rule"
                else:
                    status_string = "Not_tested"
            except Exception as exc:
                logging.error("%d generated an exception: %s" % (run_id, exc))
                traceback.print_exc()
                status_string = "exception"

            info = dict()
            info["run_id"] = run_id
            info["pass_patterns"] = pass_patterns
            info["fail_patterns"] = fail_patterns
            info["false_positive"] = false_positive
            info["false_negative"] = false_negative
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


def generate_merged_testcase(orignal_testcase, marker_testcase):
    """
    This function will merge orignal gds file with generated
    markers gds file.

    Parameters
    ----------
    orignal_testcase : string or Path object
        Path string to the orignal testcase

    marker_testcase : string or Path
        Path of the output marker gds file generated from db file.

    Returns
    -------
    merged_gds_path : string or Path
        Path of the final merged gds file generated.
    """

    new_lib = gdstk.Library()

    lib_org = gdstk.read_gds(orignal_testcase)
    lib_marker = gdstk.read_gds(marker_testcase)

    # Getting flattened top cells
    top_cell_org = lib_org.top_level()[0].flatten(apply_repetitions=True)
    top_cell_marker = lib_marker.top_level()[0].flatten(apply_repetitions=True)
    marker_polygons = top_cell_marker.get_polygons(apply_repetitions=True, include_paths=True, depth=None)

    # Merging all polygons of markers with original testcase
    for marker_polygon in marker_polygons:
        top_cell_org.add(marker_polygon)

    # Adding flattened merged cell
    new_lib.add(top_cell_org.flatten(apply_repetitions=True))

    # Writing final merged gds file
    merged_gds_path = f'{marker_testcase.replace(".gds", "")}_merged.gds'
    new_lib.write_gds(merged_gds_path)

    return merged_gds_path


def darw_polygons(polygon_data, cell, lay_num, lay_dt, path_width):
    """
    This function is used for drawing gds file with all violated polygons.

    Parameters
    ----------
    polygon_data : str
        Contains data points for each violated polygon
    cell: gdstk.cell
        Top cell will contains all generated polygons
    lay_num: int
        Number of layer used to draw violated polygons
    lay_dt : int
        Data type of layer used to draw violated polygons
    path_width : float
        Width  will used to draw edges

    Returns
    -------
    None
    """

    # Cleaning data points
    polygon_data = re.sub(r'\s+', '', polygon_data)
    polygon_data = re.sub(r'[()]', '', polygon_data)

    print("## POLYGON DATA : ", polygon_data)
    tag_split = polygon_data.split(":")
    tag = tag_split[0]
    poly_txt = tag_split[1]
    polygons = re.split(r"[/|]", poly_txt)

    logging.info(f" Type : {tag}")
    logging.info(f" All polygons {polygons}")

    # Select shape type to be drawn
    if tag == "polygon":
        for poly in polygons:
            points = [(float(p.split(",")[0]), float(p.split(",")[1])) for p in poly.split(";")]
            print("           All points : " , points)
            cell.add(gdstk.Polygon(points, lay_num, lay_dt))

    elif tag == "edge-pair":
        for poly in polygons:
            points = [(float(p.split(",")[0]), float(p.split(",")[1])) for p in poly.split(";")]
            print("           All points : " , points)
            cell.add(gdstk.FlexPath(points, path_width, layer=lay_num, datatype=lay_dt))

    elif tag == "edge":
        for poly in polygons:
            points = [(float(p.split(",")[0]), float(p.split(",")[1])) for p in poly.split(";")]
            print("           All points : " , points)
            cell.add(gdstk.FlexPath(points, path_width, layer=lay_num, datatype=lay_dt))
    else:
        logging.error(f"## Unknown type: {tag} ignored")


def convert_results_db_to_gds(results_database: str):
    """
    This function will parse Klayout database for analysis.
    It converts the lyrdb klayout database file to GDSII file

    Parameters
    ----------
    results_database : string or Path object
        Path string to the results file

    Returns
    -------
    output_gds_path : string or Path
        Path of the output marker gds file generated from db file.
    output_runset_path : string or Path
        Path of the output drc runset used for analysis.
    """

    # layer used as a marker
    rule_lay_num = 10000
    # width of edges shapes
    path_width = 0.01

    pass_marker = "input(2, 222)"
    fail_marker = "input(3, 222)"
    fail_marker2 = "input(6, 222)"
    text_marker = "input(11, 222)"

    # Generating violated rules and its points
    cell_name = ""
    lib = None
    cell = None
    in_item = False
    rule_data_type_map = list()
    analysis_rules = []

    for ev, elem in tqdm(ET.iterparse(results_database, events=('start', 'end'))):

        if elem.tag != "item" and not in_item:
            elem.clear()
            continue

        if elem.tag != "item" and in_item:
            continue

        if elem.tag == "item" and ev == "start":
            in_item = True
            continue

        rules = elem.findall("category")
        values = elem.findall("values")

        if len(values) > 0:
            polygons = values[0].findall("value")
        else:
            polygons = []

        if cell_name == "":
            all_cells = elem.findall("cell")

            if len(all_cells) > 0:
                cell_name = all_cells[0].text

                if cell_name is None:
                    elem.clear()
                    continue

                lib = gdstk.Library(f"{cell_name}_markers")
                cell = lib.new_cell(f"{cell_name}_markers")

        if len(rules) > 0:
            rule_name = rules[0].text.replace("'", "")
            if rule_name is None:
                elem.clear()
                continue

        else:
            elem.clear()
            continue

        if rule_name not in rule_data_type_map:
            rule_data_type_map.append(rule_name)

        ## Drawing polygons here.
        rule_lay_dt = rule_data_type_map.index(rule_name) + 1
        if cell is not None:
            for p in polygons:
                polygons = darw_polygons(p.text, cell, rule_lay_num, rule_lay_dt, path_width)
                break

        ## Clearing memeory
        in_item = False
        elem.clear()

        # Writing final marker gds file
        output_gds_path = f'{results_database.replace(".lyrdb", "")}_markers.gds'
        lib.write_gds(output_gds_path)

        # Writing analysis rule deck
        output_runset_path = f'{results_database.replace(".lyrdb", "")}_analysis.drc'

        runset_analysis_setup = f'''
        source($input)
        report("DRC analysis run report at", $report)
        pass_marker = {pass_marker}
        fail_marker = {fail_marker}
        fail_marker2 = {fail_marker2}
        text_marker = {text_marker}
        '''

        pass_patterns_rule = f'''
        pass_marker.interacting( text_marker.texts("{rule_name}") ).output("{rule_name}_pass_patterns", "{rule_name}_pass_patterns polygons")
        '''
        fail_patterns_rule = f'''
        fail_marker2.interacting(fail_marker.interacting(text_marker.texts("{rule_name}")) ).or( fail_marker.interacting(text_marker.texts("{rule_name}")).not_interacting(fail_marker2) ).output("{rule_name}_fail_patterns", "{rule_name}_fail_patterns polygons")
        '''
        false_pos_rule = f'''
        pass_marker.interacting(text_marker.texts("{rule_name}")).interacting(input({rule_lay_num}, {rule_lay_dt})).output("{rule_name}_false_positive", "{rule_name}_false_positive occurred")
        '''
        false_neg_rule = f'''
        ((fail_marker2.interacting(fail_marker.interacting(text_marker.texts("{rule_name}")))).or((fail_marker.interacting(input(11, 222).texts("{rule_name}")).not_interacting(fail_marker2)))).not_interacting(input({rule_lay_num}, {rule_lay_dt})).output("{rule_name}_false_negative", "{rule_name}_false_negative occurred")
        '''

        # Adding list of analysis rules
        if not any(rule_name in rule_txt for rule_txt in analysis_rules):
            analysis_rules.append(pass_patterns_rule)
            analysis_rules.append(fail_patterns_rule)
            analysis_rules.append(false_pos_rule)
            analysis_rules.append(false_neg_rule)

    with open(output_runset_path, "a+") as runset_analysis:
        # analysis_rules = list(dict.fromkeys(analysis_rules))
        runset_analysis.write(runset_analysis_setup)
        runset_analysis.write("".join(analysis_rules))

    return output_gds_path, output_runset_path


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
    test_paths = []
    # layer num of rule text
    lay_num = 11
    # layer data type of rule text
    lay_dt = 222

    # Getting all rules names from testcases
    for gds_file in gds_files:
        library = gdstk.read_gds(gds_file)
        top_cells = library.top_level()  # Get top cells
        for cell in top_cells:
            flatten_cell = cell.flatten()
            # Get all text labels for each cell
            labels = flatten_cell.get_labels(apply_repetitions=True, depth=None, layer=lay_num, texttype=lay_dt)
            # Get label value
            for label in labels:
                rule = label.text
                if rule not in rules:
                    rules.append(rule)
                    test_paths.append(gds_file)

    tc_df = pd.DataFrame({"test_path": test_paths, "rule_name": rules})
    tc_df["table_name"] = tc_df["test_path"].apply(
        lambda x: x.name.replace(".gds", "")
    )
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
    if target_rule is not None:
        tc_df = tc_df[tc_df["rule_name"] == target_rule]

    if target_table is not None:
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
    tc_df["run_id"] = list(range(len(tc_df)))
    tc_df.drop_duplicates(inplace=True)
    print(tc_df)

    tc_df.to_csv(os.path.join(output_path, "all_test_cases.csv"), index=False)

    ## Do some test cases coverage analysis
    cov_df = analyze_test_patterns_coverage(rules_df, tc_df, output_path)
    cov_df.drop_duplicates(inplace=True)
    print(cov_df)

    ## Run all test cases
    all_tc_df = run_all_test_cases(tc_df, output_path, cpu_count)
    all_tc_df.drop_duplicates(inplace=True)
    print(all_tc_df)
    all_tc_df.to_csv(
        os.path.join(output_path, "all_test_cases_results.csv"), index=False
    )

    ## Check if there any rules that generated false positive or false negative
    failing_results = all_tc_df[
        ~all_tc_df["run_status"].isin(["Passed_rule", "Not_tested"])
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
    cpu_count = os.cpu_count() if args["--mp"] is None else int(args["--mp"])

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
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Calling main function
    run_status = main(
        drc_dir, rules_dir, output_path, target_table, target_rule
    )
