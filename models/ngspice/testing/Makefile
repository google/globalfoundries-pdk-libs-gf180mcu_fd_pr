# Copyright 2022 Efabless Corporation
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

#=================================================================
# ------------------------ models_ngspice ------------------------
#=================================================================

SHELL := /bin/bash
Testing_DIR ?= $(shell pwd)
run_folder  := $(shell date +'run_%Y_%m_%d_%H:%M:%S')


.DEFAULT_GOAL := all

all : test-models_ngspice

test-models_ngspice: smoke-test models-MOS  models-BJT models-diode models-MOSCAP models-MIMCAP models-RES 

#================================
#---------- Create Run ----------
#================================

.ONESHELL:
Add_run-dir:
	@cd $(Testing_DIR)
	@ [ ! -d "$(run_folder)/" ] && cp -rf $(Testing_DIR)/regression $(Testing_DIR)/$(run_folder)

#================================
#---------- smoke-test ----------
#================================

.ONESHELL:
smoke-test:
	@echo "========== Runing models_xyce SMOKE TEST regression =========="
	@cd $(Testing_DIR)/smoke_test
	@python3 ng_smoke_test.py

#================================
# ---------- models-MOS----------
#================================

.ONESHELL:
models-MOS: Add_run-dir
	@cd $(Testing_DIR)/$(run_folder)/mos_iv_vgs
	@echo "========== Runing models_ngspice-MOS-VGS regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log
	@cd $(Testing_DIR)/$(run_folder)/mos_iv_vbs
	@echo "========== Runing models_ngspice-MOS-VBS regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log 	 
	@cd $(Testing_DIR)/$(run_folder)/mos_cv
	@echo "========== Runing models_ngspice-MOS-CV regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log 	
# @cd ../mos_iv_vbs
# @python3 models_regression.py |& tee -a ../run_log.log  

# .ONESHELL:
# clean-models-MOS:
# 	@echo "==== Cleaning models-MOS old runs ===="
# 	@cd $(Testing_DIR)/$(run_folder)/mos_iv_vgs && rm -rf nmos_* pmos_*

#================================
# ---------- models-BJT----------
#================================

.ONESHELL:
models-BJT: Add_run-dir
	@cd $(Testing_DIR)/$(run_folder)/bjt_cj
	@echo "========== Runing models_ngspice-BJT-cj regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log
	@cd $(Testing_DIR)/$(run_folder)/bjt_iv
	@echo "========== Runing models_ngspice-BJT-iv regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log
	@cd $(Testing_DIR)/$(run_folder)/bjt_beta
	@echo "========== Runing models_ngspice-BJT-beta regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log
# .ONESHELL:
# clean-models-BJT:
# 	@echo "==== Cleaning models-BJT old runs ===="
# 	@cd $(Testing_DIR)/$(run_folder)/bjt_cj && rm -rf vnpn_* vpnp_*

#================================
# --------- models-diode --------
#================================

.ONESHELL:
models-diode: Add_run-dir
	@cd $(Testing_DIR)/$(run_folder)/diode
	@echo "========== Runing models_ngspice-didoe regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log


# .ONESHELL:
# clean-models-diode:
# 	@echo "==== Cleaning models-diode old runs ===="
# 	@cd $(Testing_DIR)/$(run_folder)/diode && rm -rf np_* pn_* nwp* dnw* sc_*

#================================
# -------- models-MOSCAP --------
#================================

.ONESHELL:
models-MOSCAP: Add_run-dir
	@cd $(Testing_DIR)/$(run_folder)/moscap_c
	@echo "========== Runing models_ngspice-MOSCAP regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log


# .ONESHELL:
# clean-models-MOSCAP:
# 	@echo "==== Cleaning models-MOSCAP old runs ===="
# 	@cd $(Testing_DIR)/$(run_folder)/moscap_c && rm -rf nmoscap_* pmoscap_*	

#================================
# -------- models-MIMCAP --------
#================================

.ONESHELL:
models-MIMCAP: Add_run-dir
	@cd $(Testing_DIR)/$(run_folder)/mimcap_c
	@echo "========== Runing models_ngspice-MIMCAP regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log


# .ONESHELL:
# clean-models-MIMCAP:
# 	@echo "==== Cleaning models-MIMCAP old runs ===="
# 	@cd $(Testing_DIR)/$(run_folder)/mimcap_c && rm -rf mim*		


#================================
# --------- models-RES ----------
#================================

.ONESHELL:
models-RES: Add_run-dir
	@cd $(Testing_DIR)/$(run_folder)/resistor_r
	@echo "========== Runing models_ngspice-RES regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log


# .ONESHELL:
# clean-models-RES:
# 	@echo "==== Cleaning models-RES old runs ===="
# 	@cd $(Testing_DIR)/$(run_folder)/resistor_r && rm -rf nplus* pplus* npoly* ppoly* rm* tm* nwell



# #===============================
# # --------- Clean ALL ----------
# #===============================

# .ONESHELL:
# clean: clean-models-MOS clean-models-BJT clean-models-diode clean-models-MOSCAP clean-models-MIMCAP clean-models-RES
# 	@echo "==== Cleaning all runs is done ===="


#==========================
# --------- HELP ----------
#==========================

# Help Target
help:
	@echo "\n ==== The following are some of the valid targets for this Makefile ====\n"
	@echo "... all                  (the default if no target is provided)"
	@echo "... smoke-test           (To run smoke test for    an inverter)"
	@echo "... test-models_ngspice  (To run regression for all    devices)"
	@echo "... models-MOS           (To run regression for MOS    devices)"
	@echo "... models-BJT           (To run regression for BJT    devices)"
	@echo "... models-diode         (To run regression for diode  devices)"
	@echo "... models-MOSCAP        (To run regression for MOSCAP devices)"
	@echo "... models-MIMCAP        (To run regression for MIMCAP devices)"
	@echo "... models-RES           (To run regression for RES    devices)"
# @echo "... clean-models-MOS     (To clean old runs for MOS    devices)"
# @echo "... clean-models-BJT     (To clean old runs for BJT    devices)"
# @echo "... clean-models-diode   (To clean old runs for diode  devices)"
# @echo "... clean-models-MOSCAP  (To clean old runs for MOSCAP devices)"
# @echo "... clean-models-MIMCAP  (To clean old runs for MIMCAP devices)"
# @echo "... clean-models-RES     (To run regression for RES    devices)"
# @echo "... clean                (To clean all old runs)               "
   
.PHONY : help
