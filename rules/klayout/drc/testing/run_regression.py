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
Run GlobalFoundries 180nm MCU DRC Regression.

Usage:
    run_regression.py (--help| -h)
    run_regression.py (--path=<file_path>)... [--thr=<thr>] [--no_feol] [--no_beol] [--metal_top=<metal_top>] [--mim_option=<mim_option>] [--metal_level=<metal_level>] [--no_offgrid] [--run_name=<run_name>]

Options:
    --help -h                           Print this help message.
    --path=<file_path>                  The input GDS file path.
    --thr=<thr>                         The number of threads used in run.
    --no_feol                           Turn off FEOL rules from running.
    --no_beol                           Turn off BEOL rules from running.
    --metal_top=<metal_top>             Select top metal thickness option. Allowed values (6K , 9K, 11K, 30K). [default: 9K]
    --mim_option=<mim_option>           Select MIM capacitor option. Allowed values (A, B, NO_MIM). [default: NO_MIM]
    --metal_level=<metal_level>         Select the number of metal layers in stack. Allowed values (2, 3, 4, 5, 6). [default: 6]
    --no_offgrid                        Turn off OFFGRID checking rules.
    --run_name=<run_name>               Select your run name.
"""

from subprocess import check_call

from docopt import docopt
import os
import datetime
import xml.etree.ElementTree as ET
import csv
import time
import re
import pandas as pd
import logging

def call_regression(rule_deck_path, path):

    t0 = time.time()
    marker_gen = []
    rules      = []
    ly         = 0

    # set folder structure for each run
    x = f"{datetime.datetime.now()}"
    x = x.replace(" ", "_")
    name_ext = str(rule_deck_path).replace(".drc","").split("/")[-1]
    check_call(f"mkdir run_{x}_{name_ext}", shell=True)

    # Get the same rule deck with gds output
    with open(rule_deck_path, 'r') as f:
        for line in f:
            if 'GEOMETRY RULES' in line:
                break
            if ".output" in line:
                line_list = line.split(".output")
                line = line_list[0] + f".output(10000, {ly})\n"
                ly +=1
            marker_gen.append(line)

    marker_gen.append(f'\n source.layout.write("{os.getcwd()}/run_{x}_{name_ext}/merged_output.gds") \n')

    data = ''.join(marker_gen)
    data = re.sub("if\s\$report.*\n.*\.*\n.*\n.*\n.*\n.*\nend", "",data)

    # Create marker drc file
    marker_file = open(f"run_{x}_{name_ext}/markers.drc", "w")
    marker_file.write(data)
    marker_file.close()

    # Getting threads count
    if args["--thr"]:
        thrCount = args["--thr"][0]
    else:
        thrCount = os.cpu_count() * 2

    # Generate gds
    iname = path.split('.gds')
    if '/' in iname[0]:
        file = iname[0].split('/')
        check_call(f"klayout -b -r run_{x}_{name_ext}/markers.drc -rd input={path} -rd report={file[-1]}.lyrdb -rd thr={thrCount} {switches} ", shell=True)
    else:
        check_call(f"klayout -b -r run_{x}_{name_ext}/markers.drc -rd input={path} -rd report={iname[0]}.lyrdb -rd thr={thrCount} {switches} ", shell=True)

    marker_gen = []
    ly         = 0
    remove_if  = False

    # Get the small rule deck with gds output
    with open(rule_deck_path, 'r') as f:
        for line in f:
            if 'logger.info("Starting GF180MCU DENSITY DRC rules.")' in line:
                remove_if = True
            if remove_if == True:
                if 'CHIP.area' in line or 'end\n' in line and 'end #' not in line:
                    line = ''
            if 'GEOMETRY RULES' in line:
                break
            if ".output" in line:
                line_list = line.split('"')
                rules.append(line_list[1])
                name_list = line_list[1].split("_")
                rule = line_list[1]
                if "3.3V" in name_list[-1]:
                    rule = '_'.join(name_list[:-1]) + '_LV")'
                elif "5V" in name_list[-1]:
                    rule = '_'.join(name_list[:-1]) + f'_MV").or(input(11, 222).texts("{"_".join(name_list[:-1])}_5V")).or(input(11, 222).texts("{"_".join(name_list[:-1])}_MV_5V"))'
                elif "6V" in name_list[-1]:
                    rule = '_'.join(name_list[:-1]) + f'_MV").or(input(11, 222).texts("{"_".join(name_list[:-1])}_6V")).or(input(11, 222).texts("{"_".join(name_list[:-1])}_MV_6V"))'
                else:
                    rule = rule + '")'

                line = f'''(input(2, 222).interacting(input(11, 222).texts("{rule})).interacting(input(10000, {ly})).output("{line_list[1]}_false_positive", "{line_list[1]}_false_positive occurred") \n
    ((input(6, 222).interacting(input(3, 222).interacting(input(11, 222).texts("{rule}))).or((input(3, 222).interacting(input(11, 222).texts("{rule})).not_interacting(input(6, 222)))).not_interacting(input(10000, {ly})).output("{line_list[1]}_false_negative", "{line_list[1]}_false_negative occurred") \n
    CHIP.not_interacting(input(11, 222).texts("{rule}).output("{line_list[1]}_not_tested", "{line_list[1]}_not_tested")\n'''
                ly +=1
            if line.strip() == "deep":
                line = "flat"
            marker_gen.append(line)

    # Create small drc file
    marker_file = open(f"run_{x}_{name_ext}/regression.drc", "w")
    marker_file.write(''.join(marker_gen))
    marker_file.close()

    # Generate databases
    check_call(f"klayout -b -r run_{x}_{name_ext}/regression.drc -rd input=run_{x}_{name_ext}/merged_output.gds -rd report=database.lyrdb -rd thr={thrCount} {switches}", shell=True)

    mytree = ET.parse(f'run_{x}_{name_ext}/database.lyrdb')
    myroot = mytree.getroot()

    report = [["Rule_Name", "False_Positive", "False_Negative", "Total_Violations", "Not_Tested" , "Known_issues"]]
    conc = [["Rule_Name", "Status"]]

    # Initial counters 
    not_tested_c = 0
    passed       = 0
    failed       = 0
    known_issues = 0

    # Get known issues list
    known_issues_df = pd.read_csv("DRC_Known_issues.csv", usecols=["Rule "])
    known_issues_list = known_issues_df["Rule "].tolist()

    for lrule in rules:

        # Values of each rule in results
        not_run         = 1        
        not_tested      = 0        
        falseNeg        = 0
        falsePos        = 0
        total_violation = 0

        # Check whether the rule was run or not
        for z in myroot[5]:
            if f"{lrule}_not_tested" == f"{z[0].text}":
                not_run = 0
                break

        # Loop on database to get the violations of required rule
        for z in myroot[7]:
            if f"'{lrule}_not_tested'" == f"{z[1].text}" or not_run == 1:#(f"{rule}" in f"{z[1].text}") and ("tested" in f"{z[1].text}"):
                not_tested += 1
                break
            else:
                if f"'{lrule}_false_positive'" == f"{z[1].text}":#(f"{rule}" in f"{z[1].text}") and ("positive" in f"{z[1].text}"):
                    falsePos += 1
                if f"'{lrule}_false_negative'" == f"{z[1].text}":#(f"{rule}" in f"{z[1].text}") and ("negative" in f"{z[1].text}"):
                    falseNeg += 1
        
        # failed rules 
        total_violation = falsePos + falseNeg
        
        report.append([lrule, falsePos, falseNeg, total_violation, not_tested , known_issues])
        if total_violation == 0 and not_tested == 0:
            conc.append([lrule, "Pass"])
            passed += 1
        elif not_tested != 0:
            conc.append([lrule, "Not_Tested"])
            not_tested_c += 1
        elif lrule in known_issues_list:
            conc.append([lrule, "known_issues"])
            known_issues +=1
        else:
            conc.append([lrule, "Fail"])
            failed += 1

    # Create final reports files
    with open(f'run_{x}_{name_ext}/report.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(report)

    with open(f'run_{x}_{name_ext}/conclusion.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(conc)

    logging.info(f"========= Summary Report in {name_ext} for {path} =========")
    logging.info(f"Total rules: {len(conc)}")
    logging.info(f"{not_tested_c} not tested rules")    
    logging.info(f"{passed} passed rules ")
    logging.info(f"{known_issues} known_issues rules ")
    logging.info(f"{failed} failed rules ")
    
    t1 = time.time()
    logging.info(f'Execution time {t1 - t0} s')
    logging.info(f"===============================================================")

    if failed > 0:
        logging.info("Some unit tests has failed. Failing regression:")
        df = pd.read_csv(f'run_{x}_{name_ext}/conclusion.csv')
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option("max_colwidth", None)
        pd.set_option('display.width', 1000)
        logging.info("## Full report:")
        print(df)

        print("\n")
        logging.info("## Only failed")
        print(df[df["Status"] == "Fail"])

        exit(1)
    return report

if __name__ == "__main__":

    # logs format
    logging.basicConfig(level=logging.DEBUG, format=f"%(asctime)s | %(levelname)-7s | %(message)s", datefmt='%d-%b-%Y %H:%M:%S')

    # Initial values for DRC report
    sub_report   = []
    full_report  = []
    final_report = [["Rule_Name", "Status"]]
    final_detailed_report = [["Rule_Name", "False_Postive", "False_Negative", "Total_Violations", "Not_Tested" , "Known_issues"]]

    # Start of execution time 
    t0 = time.time()

    # Reading docopt arguments
    args = docopt(__doc__)

    # DRC switches definitions 
    switches = ''

    if args["--no_feol"]:
        switches = switches + '-rd feol=false '
    else:
        switches = switches + '-rd feol=true '

    if args["--no_beol"]:
        switches = switches + '-rd beol=false '
    else:
        switches = switches + '-rd beol=true '

    if args["--no_offgrid"]:
        switches = switches + '-rd offgrid=false '
    else:
        switches = switches + '-rd offgrid=true '

    if args["--metal_top"] in ["6K" , "9K", "11K", "30K"]:
        switches = switches + f'-rd metal_top={args["--metal_top"]} '
    else:
        logging.error("Top metal thickness allowed values are (6K , 9K, 11K, 30K) only")
        exit()

    if args["--mim_option"] in ["A" , "B", "NO_MIM"]:
        switches = switches + f'-rd mim_option={args["--mim_option"]} '
    else:
        logging.error("MIM capacitor option allowed values are (A, B, NO_MIM) only")
        exit()

    if args["--metal_level"] in ["2" , "3", "4", "5" , "6"]:
        switches = switches + f'-rd metal_level={args["--metal_level"]}LM '
    else:
        logging.error("The number of metal layers in stack allowed values are (2, 3, 4, 5, 6) only")
        exit()

    # Starting regression     
    # Getting drc rule decks
    rule_deck_path = []
    files = os.listdir(f'..')
    for file in files:
        if ".drc" in file:
            rule_deck_path.append(f"../{file}")

    # Running regression
    for path in args["--path"]:
        for runset in rule_deck_path:
            return_report = call_regression(runset, path)
            sub_report += return_report[1:]
        full_report.append(sub_report)
        sub_report = []

    rule_num = 0

    for rule in full_report[0]:
        fail = 0
        no_test = 1
        falseNeg = 0
        falsePos = 0
        for file in range(len(full_report)):
            falsePos = falsePos + full_report[file][rule_num][1]
            falseNeg = falseNeg + full_report[file][rule_num][2]
            fail = fail + full_report[file][rule_num][3]
            no_test = no_test * full_report[file][rule_num][4]

        final_detailed_report.append([rule[0], falsePos, falseNeg, fail, no_test])

        if fail == 0 and no_test == 0:
            final_report.append([rule[0], "Pass"])
        elif no_test != 0:
            final_report.append([rule[0], "Not_Tested"])
        else:
            final_report.append([rule[0], "Fail"])
        rule_num += 1

    run_name = args["--run_name"]

    with open(f'final_detailed_report_{run_name}.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(final_detailed_report)

    with open(f'final_report_{run_name}.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(final_report)

    #  End of execution time 
    t1 = time.time()
    logging.error(f'Total execution time {t1 - t0} s')
