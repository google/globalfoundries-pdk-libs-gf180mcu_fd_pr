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

"""Run GlobalFoundries 180nm MCU SC LVS Regression.

Usage:
    run_sc_regression.py (--help| -h)
    run_sc_regression.py (--path=<file_path>)... (--run_dir=<run_dir>) [--num_cores=<num>]

Options:
    --help -h               Print this help message.
    --path=<file_path>      The input name of GDS/Netlist file path without extention.
    --run_dir=<run_dir>     Selecting your output path.
    --num_cores=<num>       Number of cores to be used by LVS checker
"""

from subprocess import check_call

from docopt import docopt
import os
import concurrent.futures
import glob
import shutil
import re
import pandas as pd
import numpy as np
import time
import logging


def lvs_check(sc_input):

    # print(f"================================================")
    # print ('{:-^48}'.format(sc_input.upper()))
    # print(f"================================================ \n")

    # Selecting correct netlist
    if "gf180mcu_fd_io_" in sc_input:
        cdl_input = sc_input[:-4]
        cdl_input_clean = cdl_input.split("/")[-1]
        dir = "ip"
    else:
        cdl_input = sc_input
        cdl_input_clean = sc_input.split("/")[-1]
        dir = "ip"

    if "sc" in sc_input:
        sc_input_clean = sc_input.split("/")[-1]
        cdl_input = f"sc_netlists/{sc_input_clean}"
        dir = "sc"

    # Cleaning netlist [Remove unnecessary chars] and writing it again
    unnecessary_chars = ["$SUB=", "$[", "]", "$"]

    if "sc" in sc_input and "io" not in sc_input:

        with open(f"sc_testcases/sc_split/{cdl_input}.cdl", "r") as file:
            spice_netlist = file.read()
        for char in unnecessary_chars:
            spice_netlist = spice_netlist.replace(char, "")

        with open(f"sc_testcases/sc_split/{cdl_input}_modified.cdl", "w") as file:
            file.write(spice_netlist)

        cdl_input_clean = cdl_input
    else:
        with open(f"ip_testcases/{cdl_input}.cdl", "r") as file:
            spice_netlist = file.read()
        for char in unnecessary_chars:
            spice_netlist = spice_netlist.replace(char, "")

        with open(f"ip_testcases/{cdl_input}_modified.cdl", "w") as file:
            file.write(spice_netlist)

    sc_input_clean = sc_input.split("/")[-1]

    # Running LVS
    result = os.popen(
        f"klayout -b -r ../gf180mcu.lvs -rd input={dir}_testcases/{sc_input}.gds -rd report={sc_input_clean}.lvsdb -rd schematic={cdl_input_clean}_modified.cdl -rd thr={workers_count} -rd schematic_simplify=true"
    ).read()

    # moving all reports to run dir
    # check_call(f"cd {out_dir} && mkdir {sc_input_clean}")
    # check_call(f"mv -f sc_testcases/{sc_input}.lvsdb sc_testcases/*/{cdl_input_clean}_extracted.cir sc_testcases/*/{cdl_input_clean}_modified.cdl {out_dir}/{sc_input_clean}/")

    if "INFO : Congratulations! Netlists match." in result:
        logging.info("Extraction of {:<25s} has passed".format(sc_input_clean))

        with open(f"{dir}_testcases/{dir}_report.csv", "a+") as rep:
            rep.write(f"{sc_input_clean},passed\n")
    else:
        logging.info("Extraction of {:<25s} has failed".format(sc_input_clean))

        with open(f"{dir}_testcases/{dir}_report.csv", "a+") as rep:
            rep.write(f"{sc_input_clean},failed\n")


def main():

    # Remove old reports
    check_call("rm -rf sc_testcases/sc_report.csv", shell=True)
    check_call("rm -rf ip_testcases/ip_report.csv", shell=True)

    cell_list = arguments["--path"]
    if isinstance(cell_list, str):
        cell_list = [cell_list]

    sc_result = []
    get_line = False

    # Split standard cells top-cells into multiple gds files
    for cell in cell_list:
        if "sc" in cell:
            # Create GDS splitter script
            if os.path.exists("sc_testcases/sc_split") and os.path.isdir(
                "sc_testcases/sc_split"
            ):
                shutil.rmtree("sc_testcases/sc_split")
            with open("sc_testcases/split_gds.rb", "w") as f:
                f.write(
                    """ layout = RBA::Layout::new
                            layout.read($input)
                            Dir.mkdir("sc_testcases/sc_split") unless File.exists?("sc_testcases/sc_split")

                            layout.each_cell do |cell|
                                ly2 = RBA::Layout.new
                                ly2.dbu = layout.dbu
                                cell_index = layout.cell_by_name("#{cell.name}")
                                new_top = ly2.add_cell("#{cell.name}")
                                ly2.cell(new_top).copy_tree(layout.cell("#{cell.name}"))
                                ly2.write("sc_testcases/sc_split/#{cell.name}.gds")
                            end"""
                )
            check_call(
                f"klayout -b -r sc_testcases/split_gds.rb -rd input={cell}.gds",
                shell=True,
            )
            check_call("rm -rf sc_testcases/split_gds.rb", shell=True)

            # Create cdl splitter script
            cdl = cell.split("/")[-1]
            os.makedirs("sc_testcases/sc_split/sc_netlists/", exist_ok=False)
            with open(f"sc_testcases/{cdl}.cdl", "r") as cdl1:
                for line in cdl1:
                    if ".SUBCKT" in line:
                        get_line = True
                        sc_result = []
                    if get_line:
                        sc_result.append(line)
                    if ".ENDS" in line:
                        get_line = False
                        name = re.findall(".SUBCKT (/w+)", sc_result[0])
                        with open(
                            f"sc_testcases/sc_split/sc_netlists/{name[0]}.cdl", "w"
                        ) as out_cdl:
                            out_cdl.write("".join(sc_result))

    with concurrent.futures.ProcessPoolExecutor(max_workers=workers_count) as executor:
        for cell in cell_list:
            # Split standard cells top-cells into multiple gds files
            if "sc" not in cell:
                if "io" in cell:
                    cells_splitted = glob.glob(f"{cell}/*.gds")
                    for cell_split in cells_splitted:
                        cell_split_clean = cell_split.replace(".gds", "").replace(
                            "ip_testcases/", ""
                        )
                        executor.submit(lvs_check, cell_split_clean)
                else:
                    cell_clean = cell.replace("ip_testcases/", "")
                    executor.submit(lvs_check, cell_clean)

            # Running LVS on SC
            else:
                sc_list = glob.glob("sc_testcases/sc_split/*")
                for sc in sc_list:
                    sc_clean = sc.split(".gds")[0].split("sc_testcases/")[-1]
                    executor.submit(lvs_check, sc_clean)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    if os.path.isfile("sc_testcases/sc_report.csv"):
        df = pd.read_csv("sc_testcases/sc_report.csv")
        df.columns = ["CELL NAME", "RESULT"]
        df.to_csv("sc_testcases/sc_report.csv", index=False)
        df = pd.read_csv("sc_testcases/sc_report.csv")
        pass_count = df["RESULT"].str.count("passed").sum()
        fail_count = df["RESULT"].str.count("failed").sum()

        print(df)

        logging.info("\n==================================")
        logging.info(f"NO. OF PASSED SC CELLS : {pass_count}")
        logging.info(f"NO. OF FAILED SC CELLS : {fail_count}")
        logging.info("==================================\n")

        # Move split files into run dir
        shutil.move("sc_testcases/sc_report.csv", out_dir)
        shutil.move("sc_testcases/sc_split/", out_dir)

        if fail_count > 0:
            logging.info("## There are failed cases will exit with 1.")
            print(df[df["RESULT"] == "failed"])
            exit(1)

    elif os.path.isfile("ip_testcases/ip_report.csv"):
        df = pd.read_csv("ip_testcases/ip_report.csv")
        df.columns = ["CELL NAME", "RESULT"]
        df.to_csv("ip_testcases/ip_report.csv", index=False)
        df = pd.read_csv("ip_testcases/ip_report.csv")
        pass_count = df["RESULT"].str.count("passed").sum()
        fail_count = df["RESULT"].str.count("failed").sum()

        print(df)

        logging.info("\n==================================")
        logging.info(f"NO. OF PASSED IP CELLS : {pass_count}")
        logging.info(f"NO. OF FAILED IP CELLS : {fail_count}")
        logging.info("==================================\n")

        # Move files into run dir
        shutil.move("ip_testcases/ip_report.csv", out_dir)

        if fail_count > 0:
            logging.info("## There are failed cases will exit with 1.")
            print(df[df["RESULT"] == "failed"])
            exit(1)

    else:
        logging.info("\n==================================")
        logging.info("Regression Test is failed")
        logging.info("==================================\n")


if __name__ == "__main__":

    # logs format
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Args
    arguments = docopt(__doc__, version="SC LVS REGRESSION: 0.1")
    workers_count = (
        os.cpu_count() * 2
        if arguments["--num_cores"] is None
        else int(arguments["--num_cores"])
    )

    out_dir = arguments["--run_dir"]
    # Check out_dir existance
    if os.path.exists(out_dir) and os.path.isdir(out_dir):
        pass
    else:
        logging.error("This run directory doesn't exist. Please recheck.")
        exit()

    pass_count = 0
    fail_count = 0

    # Calling main function
    main()
