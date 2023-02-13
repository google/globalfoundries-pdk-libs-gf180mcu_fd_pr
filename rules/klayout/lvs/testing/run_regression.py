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
import logging
from subprocess import check_call


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
    elif len(klayout_v_list) >= 2 or len(klayout_v_list) <= 3:
        if klayout_v_list[1] < 28:
            logging.error("Prerequisites at a minimum: KLayout 0.28.0")
            logging.error(
                "Using this klayout version has not been assesed in this development. Limits are unknown"
            )
            exit(1)


def lvs_check(table, files):

    pass_count = 0
    fail_count = 0

    logging.info("================================================")
    logging.info("{:-^48}".format(table.upper()))
    logging.info("================================================ \n")

    # Get manual test cases
    x = os.popen("find man_testing/ -name *.gds").read()
    man_testing = x.split("\n")[:-1]

    # Generate databases
    for file in files:
        layout = file[0]

        # Get switches
        if layout == "sample_ggnfet_06v0_dss":
            switches = " -rd lvs_sub=sub!"
        else:
            switches = " -rd lvs_sub=vdd!"
        if len(file) > 1:
            switches = file[1] + switches

        # Check if file is mosfet or esd
        if "sample" in layout:
            net = f"{layout}.src"
        else:
            net = layout

        if os.path.exists(f"testcases/{net}.cdl"):
            # Get netlist with $ and ][
            with open(f"testcases/{net}.cdl", "r") as file:
                spice_netlist = file.read()

            # Replace the target string
            spice_netlist = spice_netlist.replace("$SUB=", "")
            spice_netlist = spice_netlist.replace("$", "")
            spice_netlist = spice_netlist.replace("[", "")
            spice_netlist = spice_netlist.replace("]", "")

            # Write the file out again
            with open(f"testcases/{layout}_generated.cdl", "w") as file:
                file.write(spice_netlist)

        result = os.popen(
            f"klayout -b -r ../gf180mcu.lvs -rd input=testcases/{layout}.gds -rd report={layout}.lvsdb -rd schematic={layout}_generated.cdl -rd target_netlist={layout}_extracted.cir -rd thr={workers_count} {switches}"
        ).read()

        # moving all reports to run dir
        out_dir = arguments["--run_dir"]
        device_dir = table.split(" ")[0]
        check_call(
            f"mv -f testcases/{layout}.lvsdb testcases/{layout}_extracted.cir testcases/{layout}_generated.cdl {out_dir}/LVS_{device_dir}/",
            shell=True,
        )

        if "INFO : Congratulations! Netlists match." in result:
            logging.info(f"Extraction of {layout} is passed")
            pass_count = pass_count + 1
        else:
            pass_before = pass_count
            fail_before = fail_count
            logging.error(
                f"Extraction of {layout} in fab provided test case is failed."
            )
            for file in man_testing:
                file_clean = file.split("/")[-1].replace(".gds", "")
                if layout == file_clean:
                    result = os.popen(
                        f"klayout -b -r ../gf180mcu.lvs -rd input={file} -rd report={layout}.lvsdb -rd schematic={layout}.cdl -rd target_netlist={layout}_extracted.cir -rd thr={workers_count} {switches}"
                    ).read()

                    dir_clean = file.replace(".gds", "")
                    check_call(
                        f"mv -f {dir_clean}.lvsdb {dir_clean}_extracted.cir {out_dir}/LVS_{device_dir}/",
                        shell=True,
                    )

                    if "INFO : Congratulations! Netlists match." in result:
                        logging.info(
                            f"Extraction of {layout} in manual test case is passed"
                        )
                        pass_count = pass_count + 1
                        break
                    else:
                        logging.error(
                            f"Extraction of {layout} in manual test case is failed"
                        )
                        fail_count = fail_count + 1
                        break
            if (pass_before == pass_count) and (fail_before == fail_count):
                logging.error(
                    f"{layout} is not in manual test case, Then extraction of {layout} is failed"
                )
                fail_count = fail_count + 1

    logging.info("==================================")
    logging.info(f"NO. OF PASSED {table} : {pass_count}")
    logging.info(f"NO. OF FAILED {table} : {fail_count}")
    logging.info("==================================\n")

    if fail_count > 0:
        return False
    else:
        return True


def main():

    ## Check Klayout version
    check_klayout_version()

    # Check out_dir existance
    out_dir = arguments["--run_dir"]
    if os.path.exists(out_dir) and os.path.isdir(out_dir):
        pass
    else:
        logging.error("This run directory doesn't exist. Please recheck.")
        exit()

    # MOSFET
    mosfet_files = [
        ["sample_pfet_06v0_dn"],
        ["sample_nfet_10v0_asym"],
        ["sample_nfet_03v3"],
        ["sample_pfet_05v0_dn"],
        ["sample_pfet_06v0"],
        ["sample_nfet_05v0"],
        ["sample_nfet_06v0"],
        ["sample_nfet_06v0_dn"],
        ["sample_pfet_10v0_asym"],
        ["sample_nfet_05v0_dn"],
        ["sample_pfet_05v0"],
        ["sample_pfet_03v3"],
        ["sample_nfet_06v0_nvt"],
    ]

    # BJT
    bjt_files = [
        ["npn_10p00x10p00"],
        ["npn_05p00x05p00"],
        ["npn_00p54x16p00"],
        ["npn_00p54x08p00"],
        ["npn_00p54x04p00"],
        ["npn_00p54x02p00"],
        ["pnp_10p00x10p00"],
        ["pnp_05p00x05p00"],
        ["pnp_10p00x00p42"],
        ["pnp_05p00x00p42"],
    ]

    # Diode
    diode_files = [
        ["diode_nd2ps_03v3"],
        ["diode_nd2ps_03v3_dn"],
        ["diode_nd2ps_06v0"],
        ["diode_nd2ps_06v0_dn"],
        ["diode_pd2nw_03v3"],
        ["diode_pd2nw_03v3_dn"],
        ["diode_pd2nw_06v0"],
        ["diode_pd2nw_06v0_dn"],
        ["diode_nw2ps_03v3"],
        ["diode_nw2ps_06v0"],
        ["diode_pw2dw_03v3"],
        ["diode_pw2dw_06v0"],
        ["diode_dw2ps_03v3"],
        ["diode_dw2ps_06v0"],
        ["sc_diode"],
    ]

    # Resistor
    resistor_files = [
        ["pplus_u"],
        ["nplus_s"],
        ["pplus_u_dw"],
        ["nplus_s_dw"],
        ["pplus_s"],
        ["pplus_s_dw"],
        ["nplus_u_dw"],
        ["nplus_u"],
        ["nwell"],
        ["pwell"],
        ["ppolyf_s"],
        ["ppolyf_u_3k", "-rd poly_res=3k"],
        ["ppolyf_s_dw"],
        ["ppolyf_u_1k", "-rd poly_res=1k"],
        ["ppolyf_u_3k_6p0_dw", "-rd poly_res=3k"],
        ["npolyf_u_dw"],
        ["ppolyf_u_3k_dw", "-rd poly_res=3k"],
        ["ppolyf_u_3k_6p0", "-rd poly_res=3k"],
        ["npolyf_s"],
        ["ppolyf_u_1k_6p0_dw", "-rd poly_res=1k"],
        ["ppolyf_u"],
        ["npolyf_u"],
        ["ppolyf_u_2k_dw", "-rd poly_res=2k"],
        ["npolyf_s_dw"],
        ["ppolyf_u_2k_6p0_dw", "-rd poly_res=2k"],
        ["ppolyf_u_2k_6p0", "-rd poly_res=2k"],
        ["ppolyf_u_dw"],
        ["ppolyf_u_1k_6p0", "-rd poly_res=1k"],
        ["ppolyf_u_2k", "-rd poly_res=2k"],
        ["ppolyf_u_1k_dw", "-rd poly_res=1k"],
        ["rm1"],
        ["rm2"],
        ["rm3"],
        ["tm6k", "-rd metal_top=6K"],
        ["tm9k", "-rd metal_top=9K"],
        ["tm30k", "-rd metal_top=30K"],
        ["tm11k", "-rd metal_top=11K"],
    ]

    # MIM Capacitor
    mim_files = [
        ["cap_mim_1f0_m2m3_noshield", "-rd mim_option=A -rd mim_cap=1"],
        ["cap_mim_1f5_m2m3_noshield", "-rd mim_option=A -rd mim_cap=1.5"],
        ["cap_mim_2f0_m2m3_noshield", "-rd mim_option=A -rd mim_cap=2"],
        ["cap_mim_1f0_m3m4_noshield", "-rd mim_option=B -rd mim_cap=1"],
        ["cap_mim_1f5_m3m4_noshield", "-rd mim_option=B -rd mim_cap=1.5"],
        ["cap_mim_2f0_m3m4_noshield", "-rd mim_option=B -rd mim_cap=2"],
        ["cap_mim_1f0_m4m5_noshield", "-rd mim_option=B -rd mim_cap=1"],
        ["cap_mim_1f5_m4m5_noshield", "-rd mim_option=B -rd mim_cap=1.5"],
        ["cap_mim_2f0_m4m5_noshield", "-rd mim_option=B -rd mim_cap=2"],
        ["cap_mim_1f0_m5m6_noshield", "-rd mim_option=B -rd mim_cap=1"],
        ["cap_mim_1f5_m5m6_noshield", "-rd mim_option=B -rd mim_cap=1.5"],
        ["cap_mim_2f0_m5m6_noshield", "-rd mim_option=B -rd mim_cap=2"]
    ]

    # MOS Capacitor
    moscap_files = [
        ["cap_pmos_03v3_b"],
        ["cap_nmos_03v3_b"],
        ["cap_nmos_03v3"],
        ["cap_nmos_06v0_b"],
        ["cap_pmos_06v0_dn"],
        ["cap_nmos_06v0"],
        ["cap_pmos_03v3_dn"],
        ["cap_pmos_06v0"],
        ["cap_nmos_03v3_dn"],
        ["cap_pmos_06v0_b"],
        ["cap_pmos_03v3"],
        ["cap_nmos_06v0_dn"],
    ]

    # ESD (SAB MOSFET)
    esd_files = [
        ["sample_pfet_05v0_dss"],
        ["sample_nfet_05v0_dss"],
        ["sample_pfet_03v3_dn_dss"],
        ["sample_pfet_03v3_dss"],
        ["sample_pfet_05v0_dn_dss"],
        ["sample_nfet_06v0_dss"],
        ["sample_pfet_06v0_dn_dss"],
        ["sample_nfet_06v0_dn_dss"],
        ["sample_nfet_03v3_dn_dss"],
        ["sample_nfet_05v0_dn_dss"],
        ["sample_nfet_03v3_dss"],
        ["sample_pfet_06v0_dss"],
    ]

    # eFuse
    efuse_files = [["efuse"]]

    logging.info("================================")
    logging.info("Running LVS regression")
    logging.info("================================\n")

    status = True
    if arguments["--device"] == "MOS":
        status = lvs_check("MOS DEVICES", mosfet_files)
    elif arguments["--device"] == "BJT":
        status = lvs_check("BJT DEVICES", bjt_files)
    elif arguments["--device"] == "DIODE":
        status = lvs_check("DIODE DEVICES", diode_files)
    elif arguments["--device"] == "RES":
        status = lvs_check("RES DEVICES", resistor_files)
    elif arguments["--device"] == "MIMCAP":
        status = lvs_check("MIMCAP DEVICES", mim_files)
    elif arguments["--device"] == "MOSCAP":
        status = lvs_check("MOSCAP DEVICES", moscap_files)
    elif arguments["--device"] == "MOS-SAB":
        status = lvs_check("MOS-SAB DEVICES", esd_files)
    elif arguments["--device"] == "EFUSE":
        status = lvs_check("EFUSE DEVICES", efuse_files)
    else:
        status = lvs_check("MOS DEVICES", mosfet_files)
        status = lvs_check("BJT DEVICES", bjt_files)
        status = lvs_check("DIODE DEVICES", diode_files)
        status = lvs_check("RES DEVICES", resistor_files)
        status = lvs_check("MIM DEVICES", mim_files)
        status = lvs_check("MOSCAP DEVICES", moscap_files)
        status = lvs_check("ESD DEVICES", esd_files)
        status = lvs_check("EFUSE DEVICES", efuse_files)

    if not status:
        logging.error(" There are failed cases will exit with 1.")
        exit(1)


if __name__ == "__main__":

    # Args
    arguments = docopt(__doc__, version="LVS REGRESSION: 0.1")
    workers_count = (
        os.cpu_count() * 2
        if arguments["--num_cores"] is None
        else int(arguments["--num_cores"])
    )

    # logs format
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Calling main function
    main()
