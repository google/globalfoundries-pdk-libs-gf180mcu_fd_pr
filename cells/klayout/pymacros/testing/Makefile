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

SHELL        := /bin/bash
Testing_DIR  ?= $(shell pwd)
run_folder   := $(shell date +'run_%Y_%m_%d_%H_%M')


.DEFAULT_GOAL := all

all : test-pcell

test-pcell: Add_run-dir test-diode  test-MIM  test-cap_mos  test-FET  test-RES

#=================================
# --------- RUN FOLDER ----------
#=================================

.ONESHELL:
Add_run-dir:
	@cd $(Testing_DIR)
	@ mkdir -p $(run_folder)/bjt  $(run_folder)/diode  $(run_folder)/cap_mim $(run_folder)/mosfet  $(run_folder)/cap_mos $(run_folder)/res


#=================================
# ---------- test-BJT --------
#=================================

.ONESHELL:
test-bjt: Add_run-dir 
	@cd $(Testing_DIR)
	@echo "===== test BJT pcells ====="
	@pytest --device=bjt pcell_reg_Pytest.py


#=================================
# -------- test-diode -------
#=================================

.ONESHELL:
test-diode: Add_run-dir
	@cd $(Testing_DIR)
	@echo "===== test diode pcells ====="
	@pytest --device=diodes pcell_reg_Pytest.py

#=================================
# --------- test-MIM ---------
#=================================

.ONESHELL:
test-MIM: Add_run-dir
	@cd $(Testing_DIR)
	@echo "===== test MIM pcells ====="
	@pytest --device=mim_caps pcell_reg_Pytest.py

#=================================
# --------- test-MOS ---------
#=================================

.ONESHELL:
test-FET : test-nfet_03v3 test-nfet_05v0 test-nfet_06v0  test-pfet_03v3 test-pfet_05v0 test-pfet_06v0 

test-nfet_03v3: Add_run-dir 
	@cd $(Testing_DIR)
	@echo "===== test nfet_03v3 pcells ====="
	@pytest --device=nfet_03v3 pcell_reg_Pytest.py

test-nfet_05v0: Add_run-dir 
	@cd $(Testing_DIR)
	@echo "===== test nfet_05v0 pcells ====="
	@pytest --device=nfet_05v0 pcell_reg_Pytest.py

test-nfet_06v0: Add_run-dir 
	@cd $(Testing_DIR)
	@echo "===== test nfet_06v0 pcells ====="
	@pytest --device=nfet_06v0 pcell_reg_Pytest.py
	
test-pfet_03v3: Add_run-dir 
	@cd $(Testing_DIR)
	@echo "===== test pfet_03v3 pcells ====="
	@pytest --device=pfet_03v3 pcell_reg_Pytest.py

test-pfet_05v0: Add_run-dir 
	@cd $(Testing_DIR)
	@echo "===== test pfet_05v0 pcells ====="
	@pytest --device=pfet_05v0 pcell_reg_Pytest.py

test-pfet_06v0: Add_run-dir 
	@cd $(Testing_DIR)
	@echo "===== test pfet_06v0 pcells ====="
	@pytest --device=pfet_06v0 pcell_reg_Pytest.py


#=================================
# ------- test-cap_mos --------
#=================================

.ONESHELL:
test-cap_mos: Add_run-dir
	@cd $(Testing_DIR)
	@echo "===== test cap_mos pcells ====="
	@pytest --device=mos_caps pcell_reg_Pytest.py

#=================================
# --------- test-RES ---------
#=================================

.ONESHELL:
test-RES: Add_run-dir
	@cd $(Testing_DIR)
	@echo "===== test res pcells ====="
	@pytest --device=res pcell_reg_Pytest.py

#==========================
# --------- HELP ----------
#==========================

# Help Target
help:
	@echo "\n ==== The following are some of the valid targets for this Makefile ====\n"
	@echo "... all                        (the default if no target is provided             )"
	@echo "... tes-pcell	             (To run DRC for on all pcells                     )"
	@echo "... test-bjt               (To run DRC for on bjt pcells                     )"
	@echo "... test-diode             (To run DRC for on diode pcells                   )"
	@echo "... test-MIM               (To run DRC for on MIM pcells                     )"
	@echo "... test-FET               (To run DRC for on FET pcells                     )"
	@echo "... test-cap_mos           (To run DRC for on cap_mos pcells                 )"
	@echo "... test-RES               (To run DRC for on RES pcells                     )"

