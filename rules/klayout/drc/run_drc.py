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
Run GlobalFoundries 180nm MCU DRC.

Usage:
    run_drc.py (--help| -h)
    run_drc.py (--path=<file_path>) (--variant=<combined_options>) [--table=<table_name>]... [--mp=<num_cores>] [--run_dir=<run_dir_path>] [--topcell=<topcell_name>] [--thr=<thr>] [--run_mode=<run_mode>] [--no_feol] [--no_beol] [--connectivity] [--density] [--density_only] [--antenna] [--antenna_only] [--no_offgrid]

Options:
    --help -h                           Print this help message.
    --path=<file_path>                  The input GDS file path.
    --variant=<combined_options>        Select combined options of metal_top, mim_option, and metal_level. Allowed values (A, B, C).
                                        variant=A: Select  metal_top=30K  mim_option=A  metal_level=3LM
                                        variant=B: Select  metal_top=11K  mim_option=B  metal_level=4LM
                                        variant=C: Select  metal_top=9K   mim_option=B  metal_level=5LM
    --topcell=<topcell_name>            Topcell name to use.
    --table=<table_name>                Table name to use to run the rule deck.
    --mp=<num_cores>                    Run the rule deck in parts in parallel to speed up the run.
    --run_dir=<run_dir_path>            Run directory to save all the results [default: pwd]
    --thr=<thr>                         The number of threads used in run.
    --run_mode=<run_mode>               Select klayout mode Allowed modes (flat , deep, tiling). [default: flat]
    --no_feol                           Turn off FEOL rules from running.
    --no_beol                           Turn off BEOL rules from running.
    --connectivity                      Turn on connectivity rules.
    --density                           Turn on Density rules.
    --density_only                      Turn on Density rules only.
    --antenna                           Turn on Antenna checks.
    --antenna_only                      Turn on Antenna checks only.
    --no_offgrid                        Turn off OFFGRID checking rules.
"""

from docopt import docopt
import os
import xml.etree.ElementTree as ET
import logging
import subprocess
import pya
import glob
from datetime import datetime
from subprocess import check_call
import shutil



def get_rules_with_violations(results_database):
    """
    This function will find all the rules that has violated in a database.

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

def check_drc_results(results_db_files: list):
    """
    check_drc_results Checks the results db generated from run and report at the end if the DRC run failed or passed.
    This function will exit with 1 if there are violations.

    Parameters
    ----------
    results_db_files : list
        A list of strings that represent paths to results databases of all the DRC runs.
    """

    full_violating_rules = set()

    for f in results_db_files:
        violating_rules = get_rules_with_violations(f)
        full_violating_rules.update(violating_rules)
    
    if len(full_violating_rules) > 0:
        logging.error("Klayout DRC run is not clean.")
        logging.error("Violated rules are : {}\n".format(str(full_violating_rules)))
        exit(1)
    else:
        logging.info("Klayout DRC run is clean. GDS has no DRC violations.")


def get_results(rule_deck, rules, lyrdb, type):

    mytree = ET.parse(f"{lyrdb}_{type}_gf{arguments['--gf180mcu']}.lyrdb")
    myroot = mytree.getroot()

    violated = []

    for lrule in rules:
        # Loop on database to get the violations of required rule
        for z in myroot[7]:
            if f"'{lrule}'" == f"{z[1].text}":
                violated.append(lrule)
                break

    lyrdb_clean = lyrdb.split("/")[-1]

    if len(violated) > 0:
        logging.error(
            f"\nTotal # of DRC violations in {rule_deck}.drc is {len(violated)}. Please check {lyrdb_clean}_{type}_gf{arguments['--gf180mcu']}.lyrdb file For more details"
        )
        logging.info("Klayout GDS DRC Not Clean")
        logging.info(f"Violated rules are : {violated}\n")
    else:
        logging.info(
            f"\nCongratulations !!. No DRC Violations found in {lyrdb_clean} for {rule_deck}.drc rule deck with switch gf{arguments['--gf180mcu']}"
        )
        logging.info("Klayout GDS DRC Clean\n")


def generate_drc_run_template(drc_dir : str, run_dir: str, run_tables_list: list =[]):
    """
    generate_drc_run_template will generate the template file to run drc in the run_dir path.

    Parameters
    ----------
    drc_dir : str
        Path string to the location where the DRC files would be found to get the list of the rule tables.
    run_dir : str
        Absolute path string to the run location where all the run output will be generated.
    deck_name : str, optional
        Name of the rule deck to use for generating the template, by default ""
    run_tables_list : list, optional
        list of target parts of the rule deck, if empty assume all of the rule tables found, by default []
    
    Returns
    -------
    str
        Absolute path to the generated DRC file.
    """
    if len(run_tables_list) < 1:
        all_tables = [os.path.basename(f) for f in glob.glob(os.path.join(drc_dir, "rule_decks", "*.drc")) if "antenna" not in f and "density" not in f and "main" not in f and "tail" not in f]
        deck_name = "main"
    elif len(run_tables_list) == 1:
        deck_name = run_tables_list[0]
        all_tables = ["{}.drc".format(run_tables_list[0])]
    else:
        all_tables = ["{}.drc".format(t) for t in run_tables_list]
        deck_name = "main"
        
    logging.info("## Generating template with for the following rule tables: {}".format(str(all_tables)))
    print(run_dir)

    all_tables.insert(0, "main.drc")
    all_tables.append("tail.drc")

    gen_rule_deck_path = os.path.join(run_dir, "{}.drc".format(deck_name))
    with open(gen_rule_deck_path,'wb') as wfd:
        for f in all_tables:
            with open(os.path.join(drc_dir, "rule_decks", f),'rb') as fd:
                shutil.copyfileobj(fd, wfd)
    
    return gen_rule_deck_path

def get_top_cell_names(gds_path):
    """
    get_top_cell_names get the top cell names from the GDS file.

    Parameters
    ----------
    gds_path : string
        Path to the target GDS file.

    Returns
    -------
    List of string
        Names of the top cell in the layout.
    """
    layout = pya.Layout()
    layout.read(gds_path)
    top_cells = [t.name for t in layout.top_cells()]
    
    return top_cells

def get_run_top_cell_name(arguments, layout_path):
    """
    get_run_top_cell_name Get the top cell name to use for running. If it's provided by the user, we use the user input.
    If not, we get it from the GDS file.

    Parameters
    ----------
    arguments : dict
        Dictionary that holds the user inputs for the script generated by docopt.
    layout_path : string
        Path to the target layout.
    
    Returns
    -------
    string
        Name of the topcell to use in run.

    """

    if arguments["--topcell"]:
        topcell = arguments["--topcell"]
    else:
        layout_topcells = get_top_cell_names(layout_path)
        if len(layout_topcells) > 1:
            logging.error("## Layout has mutliple topcells. Please determine which topcell you want to run on.")
            exit(1)
        else:
            topcell = layout_topcells[0]
    
    return topcell

def generate_klayout_switches(arguments, layout_path):
    """
    parse_switches Function that parse all the args from input to prepare switches for DRC run.

    Parameters
    ----------
    arguments : dict
        Dictionary that holds the arguments used by user in the run command. This is generated by docopt library.
    layout_path : string
        Path to the layout file that we will run DRC on.
    
    Returns
    -------
    dict
        Dictionary that represent all run switches passed to klayout.
    """
    switches = dict()

    # No. of threads
    thrCount = (
        2 if arguments["--thr"] == None else int(arguments["--thr"])
    )
    switches["thr"] = str(int(thrCount))

    if arguments["--run_mode"] in ["flat", "deep", "tiling"]:
        switches["run_mode"] = arguments["--run_mode"]
    else:
        logging.error("Allowed klayout modes are (flat , deep , tiling) only")
        exit()

    if arguments["--variant"] == "A":
        switches["metal_top"] = "30K"
        switches["mim_option"] = "A"
        switches["metal_level"] = "3LM"
        #switches = switches + f"-rd metal_top=30K -rd mim_option=A -rd metal_level=3LM "
    elif arguments["--variant"] == "B":
        switches["metal_top"] = "11K"
        switches["mim_option"] = "B"
        switches["metal_level"] = "4LM"
        #switches = switches + f"-rd metal_top=11K -rd mim_option=B -rd metal_level=4LM "
    elif arguments["--variant"] == "C":
        switches["metal_top"] = "9K"
        switches["mim_option"] = "B"
        switches["metal_level"] = "5LM"
        #switches = switches + f"-rd metal_top=9K  -rd mim_option=B -rd metal_level=5LM "
    else:
        logging.error("variant switch allowed values are (A , B, C) only")
        exit()

    if arguments["--no_feol"]:
        switches["feol"] = "false"
    else:
        switches["feol"] = "true"

    if arguments["--no_beol"]:
        switches["beol"] = "false"
    else:
        switches["beol"] = "true"

    if arguments["--no_offgrid"]:
        switches["offgrid"] = "false"
    else:
        switches["offgrid"] = "true"

    if arguments["--connectivity"]:
        switches["conn_drc"] = "true"
    else:
        switches["conn_drc"] = "false"

    if arguments["--density"]:
        switches["density"] = "true"
    else:
        switches["density"] = "false"
    
    switches["topcell"] = get_run_top_cell_name(arguments, layout_path)
    switches["input"] = layout_path

    return switches

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
        if klayout_v_list[1] <= 27:
            logging.warning(f"Prerequisites at a minimum: KLayout 0.27.8")
            logging.error(
                "Using this klayout version has not been assesed in this development. Limits are unknown"
            )
            exit(1)
    elif len(klayout_v_list) == 3:
        if klayout_v_list[1] <= 27 and klayout_v_list[2] < 8:
            logging.warning(f"Prerequisites at a minimum: KLayout 0.27.8")
            logging.error(
                "Using this klayout version has not been assesed in this development. Limits are unknown"
            )
            exit(1)
    
def check_layout_path(layout_path):
    """
    check_layout_type checks if the layout provided is GDS. Otherwise, kill the process. We only support GDS now.

    Parameters
    ----------
    layout_path : string
        string that represent the path of the layout.
    
    Returns
    -------
    string
        string that represent full absolute layout path.
    """

    if not os.path.isfile(layout_path):
        logging.error("## GDS file path provided doesn't exist or not a file.")
        exit(1)

    if not ".gds" in layout_path:
        logging.error("## Layout is not in GDSII format. Please use gds format.")
        exit(1)
    
    return os.path.abspath(layout_path)

def build_switches_string(sws: dict):
    """
    build_switches_string Build swtiches string from dictionary.

    Parameters
    ----------
    sws : dict
        Dictionary that holds the Antenna swithces.
    """
    switches_str = ""
    for k in sws:
        switches_str += "-rd {}={} ".format(k, sws[k])
    
    return switches_str

def run_check(drc_file:str, drc_name:str, path: str, run_dir: str, sws: dict):
    """
    run_antenna_check run DRC check based on DRC file provided.

    Parameters
    ----------
    drc_file : str
        String that has the file full path to run.
    path : str
        String that holds the full path of the layout.
    run_dir : str
        String that holds the full path of the run location.
    sws : dict
        Dictionary that holds all switches that needs to be passed to the antenna checks.
    
    Returns
    -------
    string
        string that represent the path to the results output database for this run.

    """

    ## Using print because of the multiprocessing
    logging.info(
        "Running Global Foundries 180nm MCU {} checks on design {} on cell {}:".format(path, drc_name, sws["topcell"])
    )

    layout_base_name = os.path.basename(path).split(".")[0]
    new_sws = sws.copy()
    report_path = os.path.join(run_dir, "{}_{}.lyrdb".format(layout_base_name, drc_name))
    new_sws["report"] = report_path
    sws_str = build_switches_string(new_sws)

    run_str = "klayout -b -r {} {}".format(
        drc_file,
        sws_str
    )

    check_call(run_str, shell=True)

    return report_path
                
def main(drc_run_dir: str, now_str: str, arguments: dict):
    """
    main function to run the DRC.

    Parameters
    ----------
    drc_run_dir : str
        String with absolute path of the full run dir.
    now_str : str
        String with the run name for logs.
    arguments : dict
        Dictionary that holds the arguments used by user in the run command. This is generated by docopt library.
    """

    # Check gds file existance
    if os.path.exists(arguments["--path"]):
        pass
    else:
        logging.error("The input GDS file path doesn't exist, please recheck.")
        exit()

    rule_deck_full_path = os.path.dirname(os.path.abspath(__file__))

    ## Check Klayout version
    check_klayout_version()

    ## Check if there was a layout provided.
    if not arguments["--path"]:
        logging.error("No provided gds file, please add one")
        exit(1)
    
    ## Check layout type
    layout_path = arguments["--path"]
    layout_path = check_layout_path(layout_path)

    ## Get run switches
    switches = generate_klayout_switches(arguments, layout_path)

    list_of_drc_files = []
    list_res_db_files = []

    ## Run Antenna if required.
    if arguments["--antenna"] or arguments["--antenna_only"]:
        drc_path = os.path.join(rule_deck_full_path, "rule_decks", "antenna.drc")
        list_of_drc_files.append(drc_path)
        list_res_db_files.append(run_check(drc_path, "antenna", layout_path, drc_run_dir, switches))

        if (arguments["--antenna_only"]):
            logging.info("## Completed running Antenna checks only.")
            exit()

    ## Run Density if required.
    if arguments["--density"] or arguments["--density_only"]:
        drc_path = os.path.join(rule_deck_full_path, "rule_decks", "density.drc")
        list_of_drc_files.append(drc_path)
        list_res_db_files.append(run_check(drc_path, "density", layout_path, drc_run_dir, switches))

        if (arguments["--density_only"]):
            logging.info("## Completed running density checks only.")
            exit()

    ## Generate run rule deck from template.
    if not arguments["--table"]:
        drc_file = generate_drc_run_template(rule_deck_full_path, drc_run_dir)
    else:
        drc_file = generate_drc_run_template(rule_deck_full_path, drc_run_dir, arguments["--table"])
    
    list_of_drc_files.append(drc_file)

    ## Run Main DRC
    list_res_db_files.append(run_check(drc_file, "main", layout_path, drc_run_dir, switches))

    ## Check run
    check_drc_results(list_res_db_files)


# ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================

if __name__ == "__main__":

    # arguments
    arguments = docopt(__doc__, version="RUN DRC: 1.0")
    
    # logs format
    now_str = datetime.utcnow().strftime("drc_run_%Y_%m_%d_%H_%M_%S")

    if arguments["--run_dir"] == "pwd" or arguments["--run_dir"] == "" or arguments["--run_dir"] is None:
        drc_run_dir = os.path.join(os.path.abspath(os.getcwd()), now_str)
    else:
        drc_run_dir = os.path.abspath(arguments["--run_dir"])
    
    os.makedirs(drc_run_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
        logging.FileHandler(os.path.join(drc_run_dir, "{}.log".format(now_str))),
        logging.StreamHandler()
        ],
        format=f"%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Calling main function
    main(drc_run_dir, now_str, arguments)

