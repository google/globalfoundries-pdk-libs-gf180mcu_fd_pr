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

"""Run GlobalFoundries 180nm MCU LVS Regression.

Usage:
    run_regression.py (--help| -h)
    run_regression.py (--run_dir=<out_dir>) [--num_cores=<num>] [--device=<device_name>]

Options:
    --help -h                 Print this help message.
    --run_dir=<out_dir>       Selecting your output path.
    --num_cores=<num>         Number of cores to be used by LVS checker
    --device=<device_name>    Selecting device option. Allowed values (MOS, BJT, DIODE, RES, MIMCAP, MOSCAP, MOS-SAB). [default: ALL]
"""

from docopt import docopt
import os
import time
import datetime
import logging

def lvs_check(table,files):

    ## TODO : Add run folder to save all the runs inside.

    # # set folder structure for each run
    # x = f"{datetime.datetime.now()}"
    # x = x.replace(" ", "_")

    # name_ext = str(rule_deck_path).replace(".drc","").split("/")[-1]
    # os.system(f"mkdir run_{x}_{name_ext}")

    pass_count = 0
    fail_count = 0

    logging.info(f"================================================")
    logging.info('{:-^48}'.format(table.upper()))
    logging.info(f"================================================ \n")

    # Get manual test cases
    x = os.popen("find man_testing/ -name *.gds").read()
    man_testing = x.split("\n")[:-1]

    # Generate databases
    for file in files:
        layout = file[0]

        # Get switches
        switches = ''
        if len(file) > 1:
            switches = file[1]

        # Check if file is mosfet or esd
        if "sample" in layout:
            net = f"{layout}.src"
        else:
            net = layout

        if os.path.exists(f'testcases/{net}.cdl'):
            # Get netlist with $ and ][
            with open(f'testcases/{net}.cdl', 'r') as file :
                spice_netlist = file.read()

            # Replace the target string
            spice_netlist = spice_netlist.replace('$SUB=', '')
            spice_netlist = spice_netlist.replace('$', '')
            spice_netlist = spice_netlist.replace('[', '')
            spice_netlist = spice_netlist.replace(']', '')

            # Write the file out again
            with open(f'testcases/{layout}_generated.cdl', 'w') as file:
                file.write(spice_netlist)

        result = os.popen(f"klayout -b -r ../gf180mcu.lvs -rd input=testcases/{layout}.gds -rd report={layout}.lvsdb -rd schematic={layout}_generated.cdl -rd target_netlist={layout}_extracted.cir -rd thr={workers_count} {switches} -rd lvs_sub='vdd!'").read()

        # moving all reports to run dir
        out_dir = arguments["--run_dir"]
        device_dir = table.split(" ")[0]
        os.system(f"mv -f testcases/{layout}.lvsdb testcases/{layout}_extracted.cir testcases/{layout}_generated.cdl {out_dir}/LVS_{device_dir}/")

        if "INFO : Congratulations! Netlists match." in result:
            logging.info(f"Extraction of {layout} is passed")
            pass_count = pass_count + 1
        else:
            pass_before = pass_count
            fail_before = fail_count
            logging.error(f"Extraction of {layout} in fab provided test case is failed.")
            for file in man_testing:
                file_clean = file.split("/")[-1].replace(".gds","")
                if layout == file_clean:
                    result = os.popen(f"klayout -b -r ../gf180mcu.lvs -rd input={file} -rd report={layout}.lvsdb -rd schematic={layout}.cdl -rd target_netlist={layout}_extracted.cir -rd thr={workers_count} {switches} -rd lvs_sub='vdd!'").read()

                    dir_clean = file.replace(".gds","")
                    os.system(f"mv -f {dir_clean}.lvsdb {dir_clean}_extracted.cir {out_dir}/LVS_{device_dir}/")

                    if "INFO : Congratulations! Netlists match." in result:
                        logging.info(f"Extraction of {layout} in manual test case is passed")
                        pass_count = pass_count + 1
                        break
                    else:
                        logging.error(f"Extraction of {layout} in manual test case is failed")
                        fail_count = fail_count + 1
                        break
            if (pass_before == pass_count) and (fail_before == fail_count):
                logging.error(f"{layout} is not in manual test case, Then extraction of {layout} is failed")
                fail_count = fail_count + 1


    logging.info("\n==================================")
    logging.info(f"NO. OF PASSED {table} : {pass_count}")
    logging.info(f"NO. OF FAILED {table} : {fail_count}")
    logging.info("==================================\n")


def main():

    # logs format
    logging.basicConfig(level=logging.DEBUG, format=f"%(asctime)s | %(levelname)-7s | %(message)s", datefmt='%d-%b-%Y %H:%M:%S')


    # Check out_dir existance
    out_dir = arguments["--run_dir"]
    if os.path.exists(out_dir) and os.path.isdir(out_dir):
        pass
    else:
        logging.error("This run directory doesn't exist. Please recheck.")
        exit ()

    # MOSFET
    mosfet_files = [['sample_pmos_6p0_dw'], ['sample_nmos_10p0_asym'], ['sample_nmos_3p3'], ['sample_pmos_5p0_dw'], ['sample_pmos_6p0'], ['sample_nmos_5p0'], ['sample_nmos_6p0'], ['sample_nmos_6p0_dw'], ['sample_pmos_10p0_asym'], ['sample_nmos_5p0_dw'], ['sample_pmos_5p0'], ['sample_pmos_3p3'], ['sample_nmos_6p0_nat']]

    # BJT
    bjt_files    = [['vnpn_10x10'], ['vnpn_5x5'], ['vnpn_0p54x16'], ['vnpn_0p54x8'], ['vnpn_0p54x4'], ['vnpn_0p54x2'], ['vpnp_10x10'], ['vpnp_5x5'], ['vpnp_0p42x10'], ['vpnp_0p42x5']]

    # Diode
    diode_files  = [['np_3p3'], ['np_3p3_dw'], ['np_6p0'], ['np_6p0_dw'], ['pn_3p3'], ['pn_3p3_dw'], ['pn_6p0'], ['pn_6p0_dw'], ['nwp_3p3'], ['nwp_6p0'], ['dnwpw_3p3'], ['dnwpw_6p0'], ['dnwps_3p3'], ['dnwps_6p0'], ['sc_diode']]

    # Resistor
    resistor_files = [['pplus_u'], ['nplus_s'], ['pplus_u_dw'], ['nplus_s_dw'], ['pplus_s'], ['pplus_s_dw'], ['nplus_u_dw'], ['nplus_u'], ['nwell'], ['pwell'], ['ppolyf_s'], ['ppolyf_u_3k', '-rd poly_res=3k'], ['ppolyf_s_dw'], ['ppolyf_u_1k', '-rd poly_res=1k'], ['ppolyf_u_3k_6p0_dw', '-rd poly_res=3k'], ['npolyf_u_dw'], ['ppolyf_u_3k_dw', '-rd poly_res=3k'], ['ppolyf_u_3k_6p0', '-rd poly_res=3k'], ['npolyf_s'], ['ppolyf_u_1k_6p0_dw', '-rd poly_res=1k'], ['ppolyf_u'], ['npolyf_u'], ['ppolyf_u_2k_dw', '-rd poly_res=2k'], ['npolyf_s_dw'], ['ppolyf_u_2k_6p0_dw', '-rd poly_res=2k'], ['ppolyf_u_2k_6p0', '-rd poly_res=2k'], ['ppolyf_u_dw'], ['ppolyf_u_1k_6p0', '-rd poly_res=1k'], ['ppolyf_u_2k', '-rd poly_res=2k'], ['ppolyf_u_1k_dw', '-rd poly_res=1k'], ['rm1'], ['rm2'], ['rm3'], ['tm6k', '-rd metal_top=6K'], ['tm9k', '-rd metal_top=9K'], ['tm30k', '-rd metal_top=30K'], ['tm11k', '-rd metal_top=11K']]

    # MIM Capacitor
    mim_files = [['mim_1p0fF', '-rd mim_option=A -rd mim_cap=1'], ['mim_1p5fF', '-rd mim_option=A -rd mim_cap=1.5'], ['mim_2p0fF', '-rd mim_option=A -rd mim_cap=2'],['mim_1p0fF_tm', '-rd mim_option=B -rd mim_cap=1'], ['mim_1p5fF_tm', '-rd mim_option=B -rd mim_cap=1.5'], ['mim_2p0fF_tm', '-rd mim_option=B -rd mim_cap=2']]

    # MOS Capacitor
    moscap_files = [['pmoscap_3p3_b'], ['nmoscap_3p3_b'], ['nmoscap_3p3'], ['nmoscap_6p0_b'], ['pmoscap_6p0_dw'], ['nmoscap_6p0'], ['pmoscap_3p3_dw'], ['pmoscap_6p0'], ['nmoscap_3p3_dw'], ['pmoscap_6p0_b'], ['pmoscap_3p3'], ['nmoscap_6p0_dw']]

    # ESD (SAB MOSFET)
    esd_files = [['sample_pmos_5p0_sab'], ['sample_nmos_5p0_sab'], ['sample_pmos_3p3_dw_sab'], ['sample_pmos_3p3_sab'], ['sample_pmos_5p0_dw_sab'], ['sample_nmos_6p0_sab'], ['sample_pmos_6p0_dw_sab'], ['sample_nmos_6p0_dw_sab'], ['sample_nmos_3p3_dw_sab'], ['sample_nmos_5p0_dw_sab'], ['sample_nmos_3p3_sab'], ['sample_pmos_6p0_sab']]

    # eFuse
    efuse_files = [['efuse']]

    logging.info("\n================================")
    logging.info("Running LVS regression")
    logging.info("================================\n")

    if arguments["--device"] == "MOS":
        lvs_check ("MOS DEVICES" , mosfet_files)
    elif arguments["--device"] == "BJT":
        lvs_check ("BJT DEVICES"   , bjt_files)
    elif arguments["--device"] == "DIODE":
        lvs_check ("DIODE DEVICES" , diode_files)
    elif arguments["--device"] == "RES":
       lvs_check ("RES DEVICES" , resistor_files)
    elif arguments["--device"] == "MIMCAP":
        lvs_check ("MIMCAP DEVICES" , mim_files)
    elif arguments["--device"] == "MOSCAP":
        lvs_check ("MOSCAP DEVICES" , moscap_files)
    elif arguments["--device"] == "MOS-SAB":
        lvs_check ("MOS-SAB DEVICES" , esd_files)
    elif arguments["--device"] == "EFUSE":
        lvs_check ("EFUSE DEVICES" , efuse_files)
    else:
        lvs_check ("MOS DEVICES" , mosfet_files)
        lvs_check ("BJT DEVICES"   , bjt_files)
        lvs_check ("DIODE DEVICES" , diode_files)
        lvs_check ("RES DEVICES" , resistor_files)
        lvs_check ("MIM DEVICES" , mim_files)
        lvs_check ("MOSCAP DEVICES" , moscap_files)
        lvs_check ("ESD DEVICES" , esd_files)
        lvs_check ("EFUSE DEVICES" , efuse_files)

if __name__ == "__main__":

    # Args
    arguments     = docopt(__doc__, version='LVS REGRESSION: 0.1')
    workers_count = os.cpu_count()*2 if arguments["--num_cores"] == None else int(arguments["--num_cores"])

    # Calling main function
    main()
