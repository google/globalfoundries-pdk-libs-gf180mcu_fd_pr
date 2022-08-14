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

import os
import pandas as pd
import subprocess
import logging
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# ======================  Generation of switches patterns ====================================
def gen_patterns():

    switches = [ "--gf180mcu=A --no_feol"
                ,"--gf180mcu=A --no_beol"
                ,"--gf180mcu=A"
                ,"--gf180mcu=B"
                ,"--gf180mcu=C"
                ,"--gf180mcu=C --connectivity"
                ,"--gf180mcu=A --no_offgrid"
    ]

    expected_logs = ["FEOL is disabled"
                    ,"BEOL is disabled"
                    ,"METAL_TOP Selected is 30K"
                    ,"METAL_TOP Selected is 11K"
                    ,"METAL_TOP Selected is 9K"
                    ,"connectivity rules are disabled"
                    ,"Offgrid enabled  false"
    ]

    mydataset = {   'test_case_name': [ switches[0]+"_switch" ],
                    'switches': [ switches[0]],
                    'expected_output':['pass'],
                    'expected_logs':[ expected_logs[0]]
    }

    initial_dataframe = pd.DataFrame()

    for i,switch in enumerate(switches):

        add_list = {'test_case_name':switch+"_switch",'switches':switch,'expected_output':'pass', 'expected_logs':expected_logs[i]}
        initial_dataframe = initial_dataframe.append(add_list,ignore_index=True)

    initial_dataframe[["test_case_name","switches","expected_output","expected_logs"]].to_csv("pattern.csv",index=False)



# ================================== Running patterns and checking results ==================================


def run_switches():

    RUN_DIRECTORY = "switch_checking/run_switch_results/"
    csv_path = "pattern.csv"
    PASS = "pass"
    FAIL = "fail"
    ERROR_MESSEGE = "More than one variable for"
    LOG_FILE_NAME = "run.log"

    def run_test_case(test_case, switches, expected_result,expected_log):
        test_case = test_case.split("--")[-1]
        run_directory = RUN_DIRECTORY + test_case
        subprocess.run(['mkdir', '-p', '{0}'.format(run_directory)])

        log_file = run_directory + "/" + test_case + ".log"
        os.popen('python3 ../run_drc.py --path=switch_checking/simple_por.gds.gz {0} >> {1}'.format(switches, log_file))
        os.wait()

        proc = subprocess.Popen('grep -irn "{0}" {1}'.format(expected_log, log_file), shell=True, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        if (expected_log in str(out)) and (expected_result == PASS):
            logging.info("Switch testing of {} passed. >> {}{}\n".format(expected_log,RUN_DIRECTORY,LOG_FILE_NAME))
        else:
            logging.error("Switch testing of {} FAILD check log file for more info. >> {}{}\n".format(expected_log,RUN_DIRECTORY,LOG_FILE_NAME))

    ## read testcases from csv file
    df = pd.read_csv(csv_path)
    test_cases = df["test_case_name"]
    switches = df["switches"]
    expected_results = df["expected_output"]
    expected_log = df["expected_logs"]

    ## init log file
    subprocess.run(['mkdir', '-p', '{0}'.format(RUN_DIRECTORY)])
    subprocess.run(['touch', '{0}temp.log'.format(RUN_DIRECTORY)])
    subprocess.run(['mv', '-f', f'{RUN_DIRECTORY}temp.log', '{0}{1}'.format(RUN_DIRECTORY,LOG_FILE_NAME)])

    for test_case_index in range(0,len(test_cases)):
        test_case_switches = switches[test_case_index]

        running_msg = "running: " + "simple_por.gds.gz with " + expected_log[test_case_index] + ", switches options are: " + test_case_switches + "..."
        logging.info(running_msg)
        run_test_case(test_cases[test_case_index], test_case_switches, expected_results[test_case_index],expected_log[test_case_index])


def main():

    # logs format
    logging.basicConfig(level=logging.DEBUG, format=f"%(asctime)s | %(levelname)-7s | %(message)s", datefmt='%d-%b-%Y %H:%M:%S')

    # Remove old files
    subprocess.run(["rm", "-rf", "switch_checking/run_switch_results", "patterns.csv"])

    # Gen. patterns
    gen_patterns ()

    # Run. switches
    run_switches ()

if __name__ == "__main__":
    main()
