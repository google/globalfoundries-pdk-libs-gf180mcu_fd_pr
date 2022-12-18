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

from subprocess import check_call
import pandas as pd
import subprocess
import logging
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

# ======================  Generation of switches patterns ====================================
def gen_patterns():

    test_name = [
        "no_feol",
        "no_beol",
        "base_A_variant",
        "base_B_variant",
        "base_C_variant",
        "connectivity_enabled",
        "no_offgrid",
    ]

    switches = [
        "--gf180mcu=A --no_feol",
        "--gf180mcu=A --no_beol",
        "--gf180mcu=A",
        "--gf180mcu=B",
        "--gf180mcu=C",
        "--gf180mcu=C  --connectivity",
        "--gf180mcu=A --no_offgrid",
    ]

    expected_logs = [
        "FEOL is disabled",
        "BEOL is disabled",
        "METAL_TOP Selected is 30K",
        "METAL_TOP Selected is 11K",
        "METAL_TOP Selected is 9K",
        "connectivity rules are enabled",
        "Offgrid enabled  false",
    ]

    ds = {
        "test_case_name": test_name,
        "switches": switches,
        "expected_logs": expected_logs,
    }
    pdf = pd.DataFrame(ds)
    pdf["expected_output"] = "pass"

    pdf.to_csv("pattern.csv", index=False)
    print(pdf)


# ================================== Running patterns and checking results ==================================


def run_switches():

    RUN_DIRECTORY = "switch_checking/run_switch_results/"
    csv_path = "pattern.csv"
    PASS = "pass"
    FAIL = "fail"
    ERROR_MESSEGE = "More than one variable for"
    LOG_FILE_NAME = "run.log"

    def run_test_case(test_case, switches, expected_result, expected_log):
        try:
            test_case = test_case.split("--")[-1]
            run_directory = RUN_DIRECTORY + test_case
            check_call(f"mkdir -p {run_directory}", shell=True)

            log_file = run_directory + "/" + test_case + ".log"
            check_call(
                f"python3 ../run_drc.py --path=switch_checking/simple_por.gds.gz {switches} >> {log_file}",
                shell=True,
            )

            res = check_output_log(test_case, log_file, expected_result, expected_log)
            return res
        except Exception as e:
            print("## Run generated exception: ", test_case)
            print(str(e))
            return False

    def check_output_log(test_case, log_file, expected_result, expected_log):
        proc = subprocess.Popen(
            'grep -irn "{0}" {1}'.format(expected_log, log_file),
            shell=True,
            stdout=subprocess.PIPE,
        )
        (out, err) = proc.communicate()
        out = str(out.decode())
        if len(out) > 0 and expected_result == PASS:
            logging.info("## Found the expected log: " + str(out))
            logging.info("Test case passed. {}".format(test_case))
            logging.info(f"echo Test case passed. >> {RUN_DIRECTORY}{LOG_FILE_NAME}")
            return True
        elif len(out) < 1 and expected_result == PASS:
            logging.error(
                "Test case passed as expected but didn't generate the expected log: {}".format(
                    test_case
                )
            )
            return False
        else:
            logging.error(
                "Test case FAILD check log file for more info. {}".format(test_case)
            )
            logging.error(
                f"echo Test case FAILD check log file for more info. >> {RUN_DIRECTORY}{LOG_FILE_NAME}"
            )
            return False

    ## read testcases from csv file
    df = pd.read_csv(csv_path)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    print("## All Switch checking patterns:")
    print(df)

    test_cases = df["test_case_name"]
    switches = df["switches"]
    expected_results = df["expected_output"]
    expected_log = df["expected_logs"]

    ## init log file
    check_call(
        f"""
mkdir -p {RUN_DIRECTORY}
touch {RUN_DIRECTORY}temp.log
mv -f {RUN_DIRECTORY}temp.log {RUN_DIRECTORY}{LOG_FILE_NAME}
""",
        shell=True,
    )

    run_status = []
    sw_failed = False

    for test_case_index in range(0, len(test_cases)):
        test_case_switches = switches[test_case_index]

        running_msg = (
            "\nrunning: "
            + test_cases[test_case_index]
            + "     with switches: "
            + test_case_switches
            + "..."
        )
        logging.info(running_msg)
        check_call(
            f'echo "{running_msg}" >> {RUN_DIRECTORY}{LOG_FILE_NAME}', shell=True
        )

        case_res = run_test_case(
            test_cases[test_case_index],
            test_case_switches,
            expected_results[test_case_index],
            expected_log[test_case_index],
        )
        run_status.append(case_res)

        if not case_res:
            sw_failed = True

    df["run_status"] = run_status

    if sw_failed:
        logging.error("## One of the test cases failed. Exit with failure:")
        print(df)
        exit(1)
    else:
        logging.info("## All test cases passed.")
        logging.info("## All Switch checking patterns:")
        print(df)


def main():

    # logs format
    logging.basicConfig(
        level=logging.DEBUG,
        format=f"%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Remove old files
    check_call("rm -rf patterns.csv switch_checking/run_switch_results", shell=True)

    # Gen. patterns
    gen_patterns()

    # Run. switches
    run_switches()


if __name__ == "__main__":
    main()
