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
# ------------------------ models_xyce ------------------------
#=================================================================

SHELL := /bin/bash
Testing_DIR ?= $(shell pwd)
run_folder  := $(shell date +'run_%Y_%m_%d_%H:%M:%S')


.DEFAULT_GOAL := all

all : models-xyce smoke-test

models-xyce: models-MOS  models-BJT models-diode models-MOSCAP models-MIMCAP models-RES 

#================================
#---------- Create Run ----------
#================================

.ONESHELL:
Add_run-dir:
	@cd $(Testing_DIR)
	@ [ ! -d "$(run_folder)/" ] && mkdir $(Testing_DIR)/$(run_folder)

#================================
#---------- smoke-test ----------
#================================

.ONESHELL:
smoke-test:
	@echo "========== Runing models_xyce SMOKE TEST regression =========="
	@cd $(Testing_DIR)/smoke_test

#================================
# ---------- models-MOS----------
#================================

.ONESHELL:
models-MOS:Add_run-dir models-MOS-vgs models-MOS-vbs models-MOS-cv

.ONESHELL:
models-MOS-vgs:Add_run-dir
	@cd $(Testing_DIR)
	@cp -rf $(Testing_DIR)/regression/mos_iv_vgs  $(Testing_DIR)/$(run_folder)/mos_iv_vgs
	@cd $(Testing_DIR)/$(run_folder)/mos_iv_vgs
	@echo "========== Runing models_xyce-MOS-VGS regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log	 

.ONESHELL:
models-MOS-vbs:Add_run-dir
	@cd $(Testing_DIR)
	@cp -rf $(Testing_DIR)/regression/mos_iv_vbs  $(Testing_DIR)/$(run_folder)/mos_iv_vbs
	@cd $(Testing_DIR)/$(run_folder)/mos_iv_vbs
	@echo "========== Runing models_xyce-MOS-VBS regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log 	 	

.ONESHELL:
models-MOS-cv:Add_run-dir
	@cd $(Testing_DIR)
	@cp -rf $(Testing_DIR)/regression/mos_cv  $(Testing_DIR)/$(run_folder)/mos_cv
	@cd $(Testing_DIR)/$(run_folder)/mos_cv
	@echo "========== Runing models_xyce-MOS-CV regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log 	

#================================
# ---------- models-BJT----------
#================================

.ONESHELL:
models-BJT: Add_run-dir models-BJT-cj models-BJT-beta models-BJT-iv

.ONESHELL:
models-BJT-cj:Add_run-dir
	@cd $(Testing_DIR)
	@cp -rf $(Testing_DIR)/regression/bjt_cj  $(Testing_DIR)/$(run_folder)/bjt_cj
	@cd $(Testing_DIR)/$(run_folder)/bjt_cj
	@echo "========== Runing models_xyce-BJT-cj regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log	

.ONESHELL:
models-BJT-beta:Add_run-dir
	@cd $(Testing_DIR)
	@cp -rf $(Testing_DIR)/regression/bjt_beta  $(Testing_DIR)/$(run_folder)/bjt_beta
	@cd $(Testing_DIR)/$(run_folder)/bjt_beta
	@echo "========== Runing models_xyce-BJT-beta regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log

.ONESHELL:
models-BJT-iv:Add_run-dir
	@cd $(Testing_DIR)
	@cp -rf $(Testing_DIR)/regression/bjt_iv  $(Testing_DIR)/$(run_folder)/bjt_iv
	@cd $(Testing_DIR)/$(run_folder)/bjt_iv
	@echo "========== Runing models_xyce-BJT-iv regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log

#================================
# --------- models-diode --------
#================================

.ONESHELL:
models-diode: Add_run-dir
	@cd $(Testing_DIR)
	@cp -rf $(Testing_DIR)/regression/diode  $(Testing_DIR)/$(run_folder)/diode
	@cd $(Testing_DIR)/$(run_folder)/diode
	@echo "========== Runing models_xyce-didoe regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log

#================================
# -------- models-MOSCAP --------
#================================

.ONESHELL:
models-MOSCAP: Add_run-dir
	@cd $(Testing_DIR)
	@cp -rf $(Testing_DIR)/regression/moscap_c  $(Testing_DIR)/$(run_folder)/moscap_c
	@cd $(Testing_DIR)/$(run_folder)/moscap_c
	@echo "========== Runing models_xyce-MOSCAP regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log

#================================
# -------- models-MIMCAP --------
#================================

.ONESHELL:
models-MIMCAP: Add_run-dir
	@cd $(Testing_DIR)
	@cp -rf $(Testing_DIR)/regression/mimcap_c  $(Testing_DIR)/$(run_folder)/mimcap_c
	@cd $(Testing_DIR)/$(run_folder)/mimcap_c
	@echo "========== Runing models_xyce-MIMCAP regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log

#================================
# --------- models-RES ----------
#================================

.ONESHELL:
models-RES: Add_run-dir
	@cd $(Testing_DIR)
	@cp -rf $(Testing_DIR)/regression/resistor_r  $(Testing_DIR)/$(run_folder)/resistor_r
	@cd $(Testing_DIR)/$(run_folder)/resistor_r
	@echo "========== Runing models_xyce-RES regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log

#===============================
# --------- Clean ALL ----------
#===============================

.ONESHELL:
clean: 
	@cd $(Testing_DIR)
	@rm -rf $(Testing_DIR)/run_*
	@echo "==== Cleaning all runs is done ===="

#==========================
# --------- HELP ----------
#==========================

# Help Target
help:
	@echo "\n ==== The following are some of the valid targets for this Makefile ====\n"
	@echo "... all                  (the default if no target is provided  )"
	@echo "... smoke-test           (To run smoke test for an inverter     )"
	@echo "... models-xyce       (To run regression for all      devices)"
	@echo "... models-diode         (To run regression for diode    devices)"
	@echo "... models-MOSCAP        (To run regression for MOSCAP   devices)"
	@echo "... models-MIMCAP        (To run regression for MIMCAP   devices)"
	@echo "... models-RES           (To run regression for RES      devices)"
	@echo "... models-MOS-vgs       (To run regression for MOS-vgs  devices)"
	@echo "... models-MOS-vbs       (To run regression for MOS-vbs  devices)"
	@echo "... models-MOS-cv        (To run regression for MOS-cv   devices)"
	@echo "... models-MOS           (To run regression for MOS      devices)"
	@echo "... models-BJT-cj        (To run regression for BJT-cj   devices)"
	@echo "... models-BJT-beta      (To run regression for BJT-beta devices)"
	@echo "... models-BJT-iv        (To run regression for BJT-iv   devices)"
	@echo "... models-BJT           (To run regression for BJT      devices)"
	@echo "... clean                (To clean all old runs                 )"
   
.PHONY : help
