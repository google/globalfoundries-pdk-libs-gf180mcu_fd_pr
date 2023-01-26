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


### WARNING : This MAKEFILE IS OUT OF DATE

## TODO : Re-writing Makefile after completing DRC regression 

Testing_DIR ?= $(shell pwd)

.DEFAULT_GOAL := all

all : clean test-DRC

test-DRC: test-DRC-switch  test-DRC-SC  test-DRC-main


#=================================
# --------- test-DRC-SC ----------
#=================================
.ONESHELL:
print_klayout_version:
	@klayout -v

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
test-DRC-main : print_klayout_version 
	@python3 run_regression.py
	@echo "========== DRC-Regression is done =========="

.ONESHELL:
test-DRC-% : print_klayout_version 
	@python3 run_regression.py --table=$*
	@echo "========== DRC-Regression is done =========="

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
	@cd $(Testing_DIR)/ && rm -rf unit_tests_*
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
	@echo "... test-DRC-[table_name]  			    (To run main DRC regression on specific table     )"

