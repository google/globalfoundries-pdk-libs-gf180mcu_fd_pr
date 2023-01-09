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

#=========================================================================
# ---------------------------------- LVS ---------------------------------
#=========================================================================

SHELL        := /bin/bash
Testing_DIR  ?= $(shell pwd)
run_folder   := $(shell date +'run_%Y_%m_%d_%H_%M')

.DEFAULT_GOAL := all

all: test-LVS

test-LVS: Add_run-dir  test-LVS-switch  test-LVS-gf180mcu_fd_sc  test-LVS-main

#=================================
# --------- RUN FOLDER ----------
#=================================
.ONESHELL:
print_klayout_version:
	@klayout -v

.ONESHELL:
Add_run-dir:
	@cd $(Testing_DIR)
	@ mkdir -p $(run_folder)/switch_checking  $(run_folder)/main $(run_folder)/gf180mcu_fd_sc_mcu7t5v0 $(run_folder)/gf180mcu_fd_sc_mcu9t5v0 $(run_folder)/gf180mcu_fd_io $(run_folder)/gf180mcu_fd_ip_sram

#=================================
# --------- test-LVS-SC ----------
#=================================

.ONESHELL:
test-LVS-gf180mcu_fd_sc: print_klayout_version test-LVS-gf180mcu_fd_sc_mcu7t5v0 test-LVS-gf180mcu_fd_sc_mcu9t5v0 test-LVS-gf180mcu_fd_io test-LVS-gf180mcu_fd_ip_sram

.ONESHELL:
test-LVS-gf180mcu_fd_io: print_klayout_version Add_run-dir
	@cd $(Testing_DIR)
	@ python3 run_sc_regression.py --path=ip_testcases/gf180mcu_fd_io_3lm --path=ip_testcases/gf180mcu_fd_io_4lm --path=ip_testcases/gf180mcu_fd_io_5lm --run_dir=$(run_folder)/gf180mcu_fd_io |& tee $(run_folder)/gf180mcu_fd_io/results.log

.ONESHELL:
test-LVS-gf180mcu_fd_ip_sram: Add_run-dir
	@cd $(Testing_DIR)
	@ python3 run_sc_regression.py --path=ip_testcases/gf180mcu_fd_ip_sram__sram64x8m8wm1 --path=ip_testcases/gf180mcu_fd_ip_sram__sram128x8m8wm1 --path=ip_testcases/gf180mcu_fd_ip_sram__sram256x8m8wm1 --path=ip_testcases/gf180mcu_fd_ip_sram__sram512x8m8wm1 --run_dir=$(run_folder)/gf180mcu_fd_ip_sram |& tee $(run_folder)/gf180mcu_fd_ip_sram/results.log

.ONESHELL:
test-LVS-gf180mcu_fd_sc_mcu7t5v0: Add_run-dir
	@cd $(Testing_DIR)
	@ python3 run_sc_regression.py --path=sc_testcases/gf180mcu_fd_sc_mcu7t5v0 --run_dir=$(run_folder)/gf180mcu_fd_sc_mcu7t5v0  |& tee $(run_folder)/gf180mcu_fd_sc_mcu7t5v0/results.log

.ONESHELL:
test-LVS-gf180mcu_fd_sc_mcu9t5v0: Add_run-dir
	@cd $(Testing_DIR)
	@ python3 run_sc_regression.py --path=sc_testcases/gf180mcu_fd_sc_mcu9t5v0 --run_dir=$(run_folder)/gf180mcu_fd_sc_mcu9t5v0  |& tee $(run_folder)/gf180mcu_fd_sc_mcu9t5v0/results.log

#=================================
# ----- test-LVS_regression ------
#=================================

.ONESHELL:
test-LVS-main: print_klayout_version test-LVS_MOS  test-LVS_BJT  test-LVS_DIODE  test-LVS_RES  test-LVS_MIMCAP  test-LVS_MOSCAP  test-LVS_MOS-SAB

.ONESHELL:
test-LVS_MOS: Add_run-dir
	@cd $(Testing_DIR)
	@mkdir -p $(run_folder)/main/LVS_MOS
	@ python3 run_regression.py  --run_dir=$(run_folder)/main  --device=MOS |& tee $(run_folder)/main/LVS_MOS/results.log

.ONESHELL:
test-LVS_BJT: Add_run-dir
	@cd $(Testing_DIR)
	@mkdir -p $(run_folder)/main/LVS_BJT
	@ python3 run_regression.py  --run_dir=$(run_folder)/main --device=BJT  |& tee $(run_folder)/main/LVS_BJT/results.log

.ONESHELL:
test-LVS_DIODE: Add_run-dir
	@cd $(Testing_DIR)
	@mkdir -p $(run_folder)/main/LVS_DIODE
	@ python3 run_regression.py  --run_dir=$(run_folder)/main --device=DIODE |& tee $(run_folder)/main/LVS_DIODE/results.log

.ONESHELL:
test-LVS_RES: Add_run-dir
	@cd $(Testing_DIR)
	@mkdir -p $(run_folder)/main/LVS_RES
	@ python3 run_regression.py  --run_dir=$(run_folder)/main --device=RES |& tee $(run_folder)/main/LVS_RES/results.log

.ONESHELL:
test-LVS_MIMCAP: Add_run-dir
	@cd $(Testing_DIR)
	@mkdir -p $(run_folder)/main/LVS_MIMCAP
	@ python3 run_regression.py  --run_dir=$(run_folder)/main --device=MIMCAP |& tee $(run_folder)/main/LVS_MIMCAP/results.log

.ONESHELL:
test-LVS_MOSCAP: Add_run-dir
	@cd $(Testing_DIR)
	@mkdir -p $(run_folder)/main/LVS_MOSCAP
	@ python3 run_regression.py  --run_dir=$(run_folder)/main --device=MOSCAP |& tee $(run_folder)/main/LVS_MOSCAP/results.log

.ONESHELL:
test-LVS_MOS-SAB: Add_run-dir
	@cd $(Testing_DIR)
	@mkdir -p $(run_folder)/main/LVS_MOS-SAB
	@ python3 run_regression.py  --run_dir=$(run_folder)/main --device=MOS-SAB |& tee $(run_folder)/main/LVS_MOS-SAB/results.log

#=================================
# -------- test-LVS-switch -------
#=================================

.ONESHELL:
test-LVS-switch: print_klayout_version Add_run-dir
	@cd $(Testing_DIR)
	@cd ..
	@echo "========== LVS-Switch testing =========="
	@python3 run_lvs.py --design=testing/extraction_checking/sample_nfet_03v3.gds --net=sample_nfet_03v3.spice --gf180mcu=A  |& tee testing/$(run_folder)/switch_checking/gf180mcuA.log
	@python3 run_lvs.py --design=testing/extraction_checking/sample_nfet_03v3.gds --net=sample_nfet_03v3.spice --gf180mcu=B  |& tee testing/$(run_folder)/switch_checking/gf180mcuB.log
	@python3 run_lvs.py --design=testing/extraction_checking/sample_nfet_03v3.gds --net=sample_nfet_03v3.spice --gf180mcu=C  |& tee testing/$(run_folder)/switch_checking/gf180mcuC.log


#==========================
# --------- HELP ----------
#==========================

# Help Target
help:
	@echo "\n ==== The following are some of the valid targets for this Makefile ====\n"
	@echo "... all                  	(the default if no target is provided          )"
	@echo "... Add_run-dir          	(Create output directory of all runs           )"
	@echo "... test-LVS             	(To run LVS full regression                    )"
	@echo "... test-LVS-switch      	(To run switch checking regression             )"
	@echo "... test-LVS-gf180mcu_fd_sc	(To run standard cells LVS regression          )"
	@echo "... test-LVS-main        	(To run main LVS regression for all devices    )"
	@echo "... test-LVS_MOS         	(To run main LVS regression for MOS devices    )"
	@echo "... test-LVS_BJT         	(To run main LVS regression for BJT devices    )"
	@echo "... test-LVS_DIODE       	(To run main LVS regression for diode devices  )"
	@echo "... test-LVS_RES         	(To run main LVS regression for diode devices  )"
	@echo "... test-LVS_MIMCAP      	(To run main LVS regression for diode devices  )"
	@echo "... test-LVS_MOSCAP      	(To run main LVS regression for diode devices  )"
	@echo "... test-LVS_MOS-SAB     	(To run main LVS regression for SAB MOS devices)"
