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
from docopt import docopt
import os
import xml.etree.ElementTree as ET
import csv
import time
import concurrent.futures


def get_results(rule_deck_path, iname, file, x):
    """
    The function takes the path of the rule deck and the path of the gds file as inputs, then it runs
    the DRC using the rule deck on the gds file and returns the name of the gds file, the name of the
    rule deck, the names of the violated rules and the status of the gds file

    :param rule_deck_path: The path to the rule deck file
    :param path: The path to the GDS file you want to check
    :return: the file name, the rule deck name, the violated rules and the status of the file.
    """
    mytree = ET.parse(f"{iname[0]}_{x}.lyrdb")
    myroot = mytree.getroot()

    violated = []

    for lrule in rules:

        # Loop on database to get the violations of required rule
        for z in myroot[7]:
            if f"'{lrule}'" == f"{z[1].text}":
                violated.append(lrule)
                break

    if len(violated) > 0:
        status = "Not_clean"
    else:
        status = "Clean"

    rule_deck = rule_deck_path.split("../")

    print(f"\n The file {file[-1]} has violated rule deck {rule_deck[-1]} in: {len(violated)} rule/s which are: {violated} \n")
    print(f" The file {file[-1]} with rule deck {rule_deck[-1]} is {status} \n")
    return file[-1], rule_deck[-1], ' '.join(violated), status

def call_simulator(arg):
    """
    It runs the simulator with the given rule deck and input file, and saves the output to a database
    file

    :param rule_deck_path: The path to the rule deck file
    :param path: The path to the GDS file you want to simulate
    :param thrCount: number of threads to use
    """
    os.system(arg)

if __name__ == "__main__":

    t0 = time.time()
    args = docopt(__doc__)

    if os.path.exists("sc"):
        os.system("rm -rf sc")

    report = [["File_Name", "Rule Deck", "Rules", "Status"]]

    # Get threads count
    if args["--thr"]:
        thrCount = args["--thr"][0]
    else:
        thrCount = os.cpu_count() * 2

    os.system("klayout -v")

    rule_deck_path = []
    rules = []
    runs = []

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
            os.system(f"klayout -b -r split_gds.rb -rd input={path}")
            print(f"File {path} was splitted into multiple gds files")

    if os.path.exists("sc"):
        other_files = os.listdir('sc')
        args["--path"] = args["--path"] + other_files

    # Get input data for simulator
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
            runs.append(arg)
            x += 1

    # Run DRC
    with concurrent.futures.ProcessPoolExecutor(max_workers=thrCount) as executor:
        for run in runs:
            executor.submit(call_simulator, run)

    # Get results
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
            if os.path.exists(f"{iname[0]}_{x}.lyrdb"):
                file, rule_deck, violations, status = get_results(runset, iname, file, x)
                report.append([file, rule_deck, violations, status])
            x += 1

    with open(f'sc_drc_report.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(report)

    if os.path.exists("split_gds.rb"):
        os.remove("split_gds.rb")

    if os.path.exists("sc"):
        os.system("rm -rf sc")

    t1 = time.time()
    print(f'Total execution time {t1 - t0} s')
