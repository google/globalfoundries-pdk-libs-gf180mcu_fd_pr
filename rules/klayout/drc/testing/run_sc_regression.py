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
Run GlobalFoundries 180nm MCU DRC SC Regression.

Usage:
    run_sc_regression.py (--help| -h)
    run_sc_regression.py (--path=<file_path>)... [--thr=<thr>]

Options:
    --help -h           Print this help message
    --path=<file_path>  The input GDS file path.
    --thr=<thr>         The number of threads used in run.

"""
from subprocess import check_call

from docopt import docopt
import os
import xml.etree.ElementTree as ET
import pandas as pd
import time
import concurrent.futures


def get_results(results_file_path):
    """
    The function takes the path of the rule deck and the path of the gds file as inputs, then it runs
    the DRC using the rule deck on the gds file and returns the name of the gds file, the name of the
    rule deck, the names of the violated rules and the status of the gds file

    :param rule_deck_path: The path to the rule deck file
    :param path: The path to the GDS file you want to check
    :return: the file name, the rule deck name, the violated rules and the status of the file.
    """
    mytree = ET.parse(results_file_path)
    myroot = mytree.getroot()

    violated = []

    for lrule in rules:
        # Loop on database to get the violations of required rule
        for z in myroot[7]:
            if f"'{lrule}'" == f"{z[1].text}":
                violated.append(lrule)
                break

    if len(violated) > 0:
        status = "not_clean"
    else:
        status = "clean"

    return ' '.join(violated), len(violated), status

def call_simulator(arg):
    """
    It runs the simulator with the given rule deck and input file, and saves the output to a database
    file

    :param rule_deck_path: The path to the rule deck file
    :param path: The path to the GDS file you want to simulate
    :param thrCount: number of threads to use
    """
    try:
        check_call(arg, shell=True)
        return True
    except Exception as e:
        print("## Run generated exception: ", arg)
        print(str(e))
        return False

if __name__ == "__main__":

    t0 = time.time()
    args = docopt(__doc__)

    if os.path.exists("sc"):
        os.system("rm -rf sc")

    report_header = ["File_Name", "Rule Deck", "Rules", "Status"]

    # Get threads count
    if args["--thr"]:
        thrCount = args["--thr"][0]
    else:
        thrCount = os.cpu_count() * 2

    rule_deck_path = []
    rules = []
    runs = dict()

    files = os.listdir('..')

    for file in files:
        if ".drc" in file:
            rule_deck_path.append(f"../{file}")

    # Get rules names
    for runset in rule_deck_path:
        with open(runset, 'r') as f:
            for line in f:
                if 'GEOMETRY RULES' in line:
                    break
                if ".output" in line:
                    line_list = line.split('"')
                    rules.append(line_list[1])

    # Create GDS splitter script
    with open('split_gds.rb', 'w') as f:
        f.write(''' layout = RBA::Layout::new
                    layout.read($input)
                    Dir.mkdir("sc") unless File.exists?("sc")

                    layout.each_cell do |cell|
                        ly2 = RBA::Layout.new
                        ly2.dbu = layout.dbu
                        cell_index = layout.cell_by_name("#{cell.name}")
                        new_top = ly2.add_cell("#{cell.name}")
                        ly2.cell(new_top).copy_tree(layout.cell("#{cell.name}"))
                        ly2.write("sc/#{cell.name}.gds")
                    end''')

    # Split standard cells top-cells into multiple gds files
    for path in args["--path"]:
        iname = path.split('.gds')
        file = iname[0].split('/')
        if "sc" in file[-1]:
            print("## Extracting top cells for : ", path)
            os.system(f"klayout -b -r split_gds.rb -rd input={path}")
            print(f"File {path} was splitted into multiple gds files")
        else:
            print(f"## {path} Not a standard cells library GDS. We will use the full GDS. No splitting required.")

    ## If this was a standard cells library, get the new list of files.
    if os.path.exists("sc"):
        other_files = os.listdir('sc')
        args["--path"] = args["--path"] + other_files

    # Get input data for klayout runs and create the run list.
    for path in args["--path"]:
        x = 0
        iname = path.split('.gds')
        file = iname[0].split('/')
        if "sc" in file[-1]:
            continue
        if "/" not in path:
            path = f"sc/{path}"
        iname = path.split('.gds')
        file = iname[0].split('/')
        for runset in rule_deck_path:
            arg = f"klayout -b -r {runset} -rd input={path} -rd report={file[-1]}_{x}.lyrdb -rd thr={thrCount} -rd conn_drc=true"
            run_id = f"{runset}|{path}|{file[-1]}_{x}.lyrdb"
            runs[run_id] = arg
            x += 1

    print("## We will run klayout {} runs".format(len(runs)))

    # Run All DRC runs.
    report = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=thrCount) as executor:
        # Start the load operations and mark each future with its URL
        future_to_run_id = {executor.submit(call_simulator, runs[r]): r for r in runs}
        for future in concurrent.futures.as_completed(future_to_run_id):
            run_id = future_to_run_id[future]
            run_info = run_id.split("|")
            info = dict()
            info["file_path"] = run_info[1]
            info["runset"] = run_info[0]
            info["results_file"] = run_info[2]
            results_db_path = os.path.join(os.path.dirname(os.path.abspath(run_info[1])), run_info[2])

            try:
                run_status = future.result()
                if run_status:
                    violators, num_rules_violated, db_status = get_results(results_db_path)
                    info["rules_violated"] = violators
                    info["num_rules_violated"] = num_rules_violated
                    info["run_status"] = db_status
                else:
                    info["rules_violated"] = ""
                    info["num_rules_violated"] = 0
                    info["run_status"] = "run throws exception"

                report.append(info)

            except Exception as exc:
                print('%r generated an exception: %s' % (run_id, exc))


    df = pd.DataFrame(report)
    df.to_csv("ip_cells_run_report.csv", index=False)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option("max_colwidth", None)
    pd.set_option('display.width', 1000)

    print(df)

    if os.path.exists("split_gds.rb"):
        os.remove("split_gds.rb")

    if os.path.exists("sc"):
        os.system("rm -rf sc")

    t1 = time.time()
    print(f'Total execution time {t1 - t0} s')

    if (df["run_status"] != "clean").any():
        print("## Run failed as there are failures or violations.")
        exit(1)
    else:
        print("## Run passed with no violations or failures.")
