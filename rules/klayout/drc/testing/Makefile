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

test-DRC: test-DRC_switch  test-DRC_SC  test-DRC_main


#=================================
# --------- test-DRC_SC ----------
#=================================

.ONESHELL:
test-DRC_SC:
	@cd $(Testing_DIR)
	@echo "========== DRC-SC testing =========="
	@ python3 run_sc_regression.py --path=sc_testcases/GF018_5VGreen_SRAM_1P_64x8M8WM1.gds  \
								   --path=sc_testcases/GF018_5VGreen_SRAM_1P_128x8M8WM1.gds \
								   --path=sc_testcases/GF018_5VGreen_SRAM_1P_256x8M8WM1.gds \
								   --path=sc_testcases/GF018_5VGreen_SRAM_1P_512x8M8WM1.gds \
								   --path=sc_testcases/GF018green_ipio_5p0c_75_3lm.gds      \
								   --path=sc_testcases/GF018green_ipio_5p0c_75_4lm.gds	    \
								   --path=sc_testcases/GF018green_ipio_5p0c_75_5lm.gds 		\
								   --path=sc_testcases/GF018hv5v_green_sc9.gds 				\
								   --path=sc_testcases/GF018hv5v_mcu_sc7.gds				\

#=================================
# ----- test-DRC_regression ------
#=================================

.ONESHELL:
test-DRC_main : test-DRC-foundry-Option-1 test-DRC-foundry-Option-2 test-DRC-foundry-Option-3 test-DRC-foundry-Option-4 test-DRC-Option-A test-DRC-Option-B test-DRC-Option-C
	@echo "========== DRC-Regression is done =========="

.ONESHELL:
test-DRC-foundry-Option-1:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression foundry-Option-1 =========="
	@python3 run_regression.py --path=testcases/0.0.DM000013_13_1P6M_6kA_MIMA_SOLDER_BUMP.gds \
							   --metal_top="6K" --mim_option="A"  --metal_level=6 --run_name="DRC-foundry-Option-1"										

.ONESHELL:
test-DRC-foundry-Option-2:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression foundry-Option-2 =========="
	@python3 run_regression.py --path=testcases/0.0.DM000013_13_1P6M_9kA_MIMB_WEDGE.gds \
							   --metal_top="9K" --mim_option="B"  --metal_level=6  --run_name="DRC-foundry-Option-2"										

.ONESHELL:
test-DRC-foundry-Option-3:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression foundry-Option-3 =========="
	@python3 run_regression.py --path=testcases/0.0.DM000013_13_1P6M_11kA_MIMA_Gold_Bump.gds \
							   --metal_top="11K" --mim_option="A"  --metal_level=6	--run_name="DRC-foundry-Option-3"										

.ONESHELL:
test-DRC-foundry-Option-4:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression foundry-Option-4 =========="
	@python3 run_regression.py --path=testcases/0.0.DM000013_13_1P6M_30kA_MIMB_BALL.gds \
							   --metal_top="30K" --mim_option="B"  --metal_level=6	--run_name="DRC-foundry-Option-4"									

.ONESHELL:
test-DRC-Option-A:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression Option-A =========="
	@python3 run_regression.py --path=testcases/0.0.DM000013_13_1P6M_11kA_MIMA_Gold_Bump.gds \
							   --metal_top="30K" --mim_option="A"  --metal_level=3	--run_name="DRC-Option-A"										

.ONESHELL:
test-DRC-Option-B:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression Option-B =========="
	@python3 run_regression.py --path=testcases/0.0.DM000013_13_1P6M_11kA_MIMA_Gold_Bump.gds \
							   --metal_top="11K" --mim_option="B"  --metal_level=4	--run_name="DRC-Option-B"			

.ONESHELL:
test-DRC-Option-C:
	@cd $(Testing_DIR)
	@echo "========== DRC-Regression Option-C =========="
	@python3 run_regression.py --path=testcases/0.0.DM000013_13_1P6M_11kA_MIMA_Gold_Bump.gds \
							   --path=testcases/Manual_testcases.gds						 \
							   --path=testcases/density_testcases/Mn_4_fail.gds				 \
							   --path=testcases/density_testcases/Mn_4_pass.gds				 \
							   --path=testcases/density_testcases/MT30_7_fail.gds			 \
							   --path=testcases/density_testcases/MT30_7_pass.gds			 \
							   --path=testcases/density_testcases/MT_3_fail.gds				 \
							   --path=testcases/density_testcases/MT_3_pass.gds				 \
							   --path=testcases/density_testcases/PL_8_fail.gds				 \
							   --path=testcases/density_testcases/PL_8_pass.gds				 \
							   --metal_top="9K" --mim_option="B"  --metal_level=5	--run_name="DRC-Option-C"		

#=================================
# -------- test-DRC_switch -------
#=================================

.ONESHELL:
test-DRC_switch: 	
	@cd $(Testing_DIR)
	@echo "========== DRC-Switch testing =========="
	@python3 run_switch_checking.py
	@rm -rf pattern.csv

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
	@echo "... all                        (the default if no target is provided             )"
	@echo "... clean                      (To clean all old runs                            )"
	@echo "... test-DRC_switch            (To run switch checking regression                )"
	@echo "... test-DRC_SC                (To run standard cells DRC regression             )"
	@echo "... test-DRC_main              (To run main DRC full regression                  )"
	@echo "... test-DRC-foundry-Option-1  (To run main DRC regression using foundry-Option-1)"
	@echo "... test-DRC-foundry-Option-2  (To run main DRC regression using foundry-Option-2)"
	@echo "... test-DRC-foundry-Option-3  (To run main DRC regression using foundry-Option-3)"
	@echo "... test-DRC-foundry-Option-4  (To run main DRC regression using foundry-Option-4)"
	@echo "... test-DRC-Option-A          (To run main DRC regression using Option-A        )"
	@echo "... test-DRC-Option-B          (To run main DRC regression using Option-B        )"
	@echo "... test-DRC-Option-C          (To run main DRC regression using Option-C        )"
