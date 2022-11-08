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
# ---------------------------------- DRC ---------------------------------
#=========================================================================

Testing_DIR ?= $(shell pwd)

.DEFAULT_GOAL := all

all : clean test-DRC

test-DRC: test-DRC-switch  test-DRC-SC  test-DRC-main


#=================================
# --------- test-DRC-SC ----------
#=================================
.ONESHELL:
print_klayout_version:
	@echo "Klayout version : $(klayout -v)"

.ONESHELL:
test-DRC-SC : test-DRC-gf180mcu_fd_ip_sram test-DRC-gf180mcu_fd_io test-DRC-gf180mcu_fd_sc_mcu7t5v0 test-DRC-gf180mcu_fd_sc_mcu9t5v0
	@echo "========== DRC-DRC-SC is done =========="

.ONESHELL:
test-DRC-gf180mcu_fd_ip_sram: print_klayout_version
	@cd $(Testing_DIR)
	@echo "========== DRC-gf180mcu_fd_ip_sram testing =========="
	@ python3 run_sc_regression.py 									\
		--path=ip_testcases/gf180mcu_fd_ip_sram__sram64x8m8wm1.gds 	\
		--path=ip_testcases/gf180mcu_fd_ip_sram__sram128x8m8wm1.gds	\
		--path=ip_testcases/gf180mcu_fd_ip_sram__sram256x8m8wm1.gds	\
		--path=ip_testcases/gf180mcu_fd_ip_sram__sram512x8m8wm1.gds

.ONESHELL:
test-DRC-gf180mcu_fd_io: print_klayout_version
	@cd $(Testing_DIR)
	@echo "========== DRC-gf180mcu_fd_io testing =========="
	@ python3 run_sc_regression.py 					\
		--path=ip_testcases/gf180mcu_fd_io_3lm.gds	\
		--path=ip_testcases/gf180mcu_fd_io_4lm.gds	\
		--path=ip_testcases/gf180mcu_fd_io_5lm.gds

.ONESHELL:
test-DRC-gf180mcu_fd_sc_mcu7t5v0: print_klayout_version
	@cd $(Testing_DIR)
	@echo "========== DRC-gf180mcu_fd_sc_mcu7t5v0 testing =========="
	@ python3 run_sc_regression.py --path=sc_testcases/gf180mcu_fd_sc_mcu7t5v0.gds

.ONESHELL:
test-DRC-gf180mcu_fd_sc_mcu9t5v0: print_klayout_version
	@cd $(Testing_DIR)
	@echo "========== DRC-gf180mcu_fd_sc_mcu9t5v0 testing =========="
	@ python3 run_sc_regression.py --path=sc_testcases/gf180mcu_fd_sc_mcu9t5v0.gds

#=================================
# ----- test-DRC_regression ------
#=================================

.ONESHELL:
test-DRC-main : print_klayout_version test-DRC-foundry-Option-1 test-DRC-foundry-Option-2 test-DRC-foundry-Option-3 test-DRC-foundry-Option-4 test-DRC-Option-A test-DRC-Option-B test-DRC-Option-C
	@echo "========== DRC-Regression is done =========="

.ONESHELL:
test-DRC-foundry-Option-1:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression foundry-Option-1 =========="
	@python3 run_regression.py 																\
		--path=testcases/0.0.DM000013_13_1P6M_6kA_MIMA_SOLDER_BUMP.gds.gz					\
		--metal_top="6K" --mim_option="A"  --metal_level=6 --run_name="DRC-foundry-Option-1"

.ONESHELL:
test-DRC-foundry-Option-2:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression foundry-Option-2 =========="
	@python3 run_regression.py 																\
		--path=testcases/0.0.DM000013_13_1P6M_9kA_MIMB_WEDGE.gds.gz							\
		--metal_top="9K" --mim_option="B"  --metal_level=6  --run_name="DRC-foundry-Option-2"

.ONESHELL:
test-DRC-foundry-Option-3:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression foundry-Option-3 =========="
	@python3 run_regression.py 																\
		--path=testcases/0.0.DM000013_13_1P6M_11kA_MIMA_Gold_Bump.gds.gz					\
		--metal_top="11K" --mim_option="A"  --metal_level=6	--run_name="DRC-foundry-Option-3"

.ONESHELL:
test-DRC-foundry-Option-4:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression foundry-Option-4 =========="
	@python3 run_regression.py 																\
		--path=testcases/0.0.DM000013_13_1P6M_30kA_MIMB_BALL.gds.gz							\
		--metal_top="30K" --mim_option="B"  --metal_level=6	--run_name="DRC-foundry-Option-4"

.ONESHELL:
test-DRC-Option-A:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression Option-A =========="
	@python3 run_regression.py 														\
		--path=testcases/0.0.DM000013_13_1P6M_11kA_MIMA_Gold_Bump.gds.gz			\
		--metal_top="30K" --mim_option="A"  --metal_level=3	--run_name="DRC-Option-A"

.ONESHELL:
test-DRC-Option-B:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression Option-B =========="
	@python3 run_regression.py 														\
		--path=testcases/0.0.DM000013_13_1P6M_11kA_MIMA_Gold_Bump.gds.gz			\
		--metal_top="11K" --mim_option="B"  --metal_level=4	--run_name="DRC-Option-B"

.ONESHELL:
test-DRC-Option-C:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression Option-C =========="
	@python3 run_regression.py 														\
		--path=testcases/0.0.DM000013_13_1P6M_11kA_MIMA_Gold_Bump.gds.gz			\
		--path=testcases/Manual_testcases.gds						 				\
		--path=testcases/density_testcases/Mn_4_fail.gds				 			\
		--path=testcases/density_testcases/Mn_4_pass.gds				 			\
		--path=testcases/density_testcases/MT30_7_fail.gds			 				\
		--path=testcases/density_testcases/MT30_7_pass.gds			 				\
		--path=testcases/density_testcases/MT_3_fail.gds				 			\
		--path=testcases/density_testcases/MT_3_pass.gds				 			\
		--path=testcases/density_testcases/PL_8_fail.gds				 			\
		--path=testcases/density_testcases/PL_8_pass.gds				 			\
		--metal_top="9K" --mim_option="B"  --metal_level=5	--run_name="DRC-Option-C"

#=================================
# -------- test-DRC-switch -------
#=================================

.ONESHELL:
test-DRC-switch: print_klayout_version
	@cd $(Testing_DIR)
	@echo "========== DRC-Switch testing =========="
	python3 run_switch_checking.py && rm -rf pattern.csv

#===============================
# --------- Clean ALL ----------
#===============================

.ONESHELL:
clean:
	@echo "==== Cleaning old runs ===="
	@cd $(Testing_DIR)/ && rm -rf run_20* *report* markers.drc regression.drc merged_* sc pattern.csv database.lyrdb
	@echo "==== Cleaning all runs is done ===="

#==========================
# --------- HELP ----------
#==========================

# Help Target
help:
	@echo "\n ==== The following are some of the valid targets for this Makefile ====\n"
	@echo "... all                        			(the default if no target is provided             )"
	@echo "... clean                      			(To clean all old runs                            )"
	@echo "... test-DRC-switch            			(To run switch checking regression                )"
	@echo "... test-DRC-SC                			(To run standard cells DRC regression             )"
	@echo "... test-DRC-gf180mcu_fd_ip_sram			(To run SRAM IP cells DRC regression 	          )"
	@echo "... test-DRC-gf180mcu_fd_io				(To run I/O cells DRC regression             	  )"
	@echo "... test-DRC-gf180mcu_fd_sc_mcu7t5v0		(To run standard cells 7 tracks DRC regression    )"
	@echo "... test-DRC-gf180mcu_fd_sc_mcu9t5v0		(To run standard cells 9 tracks DRC regression    )"
	@echo "... test-DRC-main              			(To run main DRC full regression                  )"
	@echo "... test-DRC-foundry-Option-1  			(To run main DRC regression using foundry-Option-1)"
	@echo "... test-DRC-foundry-Option-2  			(To run main DRC regression using foundry-Option-2)"
	@echo "... test-DRC-foundry-Option-3  			(To run main DRC regression using foundry-Option-3)"
	@echo "... test-DRC-foundry-Option-4  			(To run main DRC regression using foundry-Option-4)"
	@echo "... test-DRC-Option-A          			(To run main DRC regression using Option-A        )"
	@echo "... test-DRC-Option-B          			(To run main DRC regression using Option-B        )"
	@echo "... test-DRC-Option-C          			(To run main DRC regression using Option-C        )"
