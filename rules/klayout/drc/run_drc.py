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
    run_drc.py (--path=<file_path>) (--gf180mcu=<combined_options>) [-run_dir=<run_dir_path>] [--topcell=<topcell_name>] [--thr=<thr>] [--run_mode=<run_mode>] [--no_feol] [--no_beol] [--connectivity] [--density] [--density_only] [--antenna] [--antenna_only] [--no_offgrid]

Options:
    --help -h                           Print this help message.
    --path=<file_path>                  The input GDS file path.
    --gf180mcu=<combined_options>       Select combined options of metal_top, mim_option, and metal_level. Allowed values (A, B, C).
                                        gf180mcu=A: Select  metal_top=30K  mim_option=A  metal_level=3LM
                                        gf180mcu=B: Select  metal_top=11K  mim_option=B  metal_level=4LM
                                        gf180mcu=C: Select  metal_top=9K   mim_option=B  metal_level=5LM
    --topcell=<topcell_name>            Topcell name to use.
    --run_dir=<run_dir_path>            Run directory to save all the results [default: pwd]
    --thr=<thr>                         The number of threads used in run.
    --run_mode=<run_mode>               Select klayout mode Allowed modes (flat , deep, tiling). [default: deep]
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
from datetime import datetime

from subprocess import check_call


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
    top_cells = [t.name for t in layout.top_cells]
    
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
        os.cpu_count() * 2 if arguments["--thr"] == None else int(arguments["--thr"])
    )
    switches["thr"] = str(int(thrCount))

    if arguments["--run_mode"] in ["flat", "deep", "tiling"]:
        switches["run_mode"] = arguments["--run_mode"]
    else:
        logging.error("Allowed klayout modes are (flat , deep , tiling) only")
        exit()

    if arguments["--gf180mcu"] == "A":
        switches["metal_top"] = "30K"
        switches["mim_option"] = "A"
        switches["metal_level"] = "3LM"
        #switches = switches + f"-rd metal_top=30K -rd mim_option=A -rd metal_level=3LM "
    elif arguments["--gf180mcu"] == "B":
        switches["metal_top"] = "11K"
        switches["mim_option"] = "B"
        switches["metal_level"] = "4LM"
        #switches = switches + f"-rd metal_top=11K -rd mim_option=B -rd metal_level=4LM "
    elif arguments["--gf180mcu"] == "C":
        switches["metal_top"] = "9K"
        switches["mim_option"] = "B"
        switches["metal_level"] = "5LM"
        #switches = switches + f"-rd metal_top=9K  -rd mim_option=B -rd metal_level=5LM "
    else:
        logging.error("gf180mcu switch allowed values are (A , B, C) only")
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
    klayout_v_ = os.popen("klayout -v").read()
    klayout_v_ = klayout_v_.split("\n")[0]
    if klayout_v_ == "":
        logging.error("Klayout is not found. Please make sure klayout is installed.")
        exit(1)
    else:
        klayout_v = int(klayout_v_.split(".")[-1])

    logging.info(f"Your Klayout version is: {klayout_v_}")

    if klayout_v < 8:
        logging.info(f"Prerequisites at a minimum: KLayout 0.27.8")
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
    """

    logging.info(
        "Running Global Foundries 180nm MCU {} checks on design {} on cell {}:".format(path, drc_name, sws["topcell"])
    )

    layout_base_name = os.path.basename(path).split(".")[0]
    new_sws = sws.copy()
    new_sws["report"] = os.path.join(run_dir, "{}_{}.lyrdb".format(layout_base_name, drc_name))
    sws_str = build_switches_string(new_sws)

    run_str = "klayout -b -r {} {}".format(
        drc_file,
        sws_str
    )

    check_call(run_str, shell=True)
                
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

    ## Run Antenna if required.
    if arguments["--antenna"] or arguments["--antenna_only"]:
        drc_path = os.path.join(rule_deck_full_path, "rule_decks", "antenna.drc")
        run_check(drc_path, "antenna", layout_path, drc_run_dir, switches)
        if (arguments["--antenna_only"]):
            logging.info("## Completed running Antenna checks only.")
            exit()

    ## Run Density if required.
    if arguments["--density"] or arguments["--density_only"]:
        drc_path = os.path.join(rule_deck_full_path, "rule_decks", "density.drc")
        run_check(drc_path, "density", layout_path, drc_run_dir, switches)
        if (arguments["--density_only"]):
            logging.info("## Completed running density checks only.")
            exit()

    ## Run Main DRC if required.
    drc_path = os.path.join(rule_deck_full_path, "rule_decks", "main.drc")
    run_check(drc_path, "main", layout_path, drc_run_dir, switches)

    
    # # ======================== Reporting results ========================
    # curr_path = os.path.dirname(os.path.abspath(__file__))
    # rule_deck_path = [
    #     f"{curr_path}/gf180mcu.drc",
    #     f"{curr_path}/gf180mcu_antenna.drc",
    #     f"{curr_path}/gf180mcu_density.drc",
    # ]

    # # Get rules from rule deck
    # rules = []

    # # Get rules from rule deck
    # for runset in rule_deck_path:
    #     with open(runset, "r") as f:
    #         for line in f:
    #             if ".output" in line:
    #                 line_list = line.split('"')
    #                 if line_list[1] in rules:
    #                     pass
    #                 else:
    #                     rules.append(line_list[1])

    # # Get results
    # lyrdbs = ["main_drc", "antenna", "density"]
    # runsets = ["gf180mcu", "gf180mcu_antenna", "gf180mcu_density"]
    # for i, lyrdb in enumerate(lyrdbs):
    #     if os.path.exists(f"{name_clean_}_{lyrdb}_gf{arguments['--gf180mcu']}.lyrdb"):
    #         get_results(runsets[i], rules, name_clean_, lyrdb)


# ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================

if __name__ == "__main__":

    # arguments
    arguments = docopt(__doc__, version="RUN DRC: 1.0")

    if arguments["--run_dir"] == "pwd" or arguments["--run_dir"] == "" or arguments["--run_dir"] is None:
        drc_run_dir = os.path.abspath(os.getcwd())
    else:
        drc_run_dir = os.path.abspath(arguments["--run_dir"])
    

    # logs format
    now_str = datetime.utcnow().strftime("drc_run_%Y_%m_%d_%H_%M_%S")

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

