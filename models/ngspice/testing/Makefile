# Copyright 2023 Efabless Corporation
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
run_folder  := $(shell date +'models_run_%Y_%m_%d_%H_%M_%S')


.DEFAULT_GOAL := all

all : models-ngspice models-smoke-test

models-ngspice: models-MOS  models-BJT models-diode models-CAP-MOS models-CAP-MIM models-RES 

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
models-smoke-test:
	@echo "========== Runing models_ngspice SMOKE TEST regression =========="
	@cd $(Testing_DIR)/smoke_test
	@python3 ng_smoke_test.py

#================================
# ---------- models-MOS----------
#================================

.ONESHELL:
models-MOS: Add_run-dir models-MOS-id models-MOS-rds models-MOS-cv

.ONESHELL:
models-MOS-id: Add_run-dir
	@cp -rf $(Testing_DIR)/regression/mos_id  $(Testing_DIR)/$(run_folder)/mos_id
	@cd $(Testing_DIR)/$(run_folder)/mos_id
	@echo "========== Runing models_ngspice-MOS-ID regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log	 

.ONESHELL:
models-MOS-rds: Add_run-dir
	@cp -rf $(Testing_DIR)/regression/mos_rds  $(Testing_DIR)/$(run_folder)/mos_rds
	@cd $(Testing_DIR)/$(run_folder)/mos_rds
	@echo "========== Runing models_ngspice-MOS-RDS regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log 	 	

.ONESHELL:
models-MOS-cv: Add_run-dir
	@cp -rf $(Testing_DIR)/regression/mos_cv  $(Testing_DIR)/$(run_folder)/mos_cv
	@cd $(Testing_DIR)/$(run_folder)/mos_cv
	@echo "========== Runing models_ngspice-MOS-CV regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log 	

#================================
# ---------- models-BJT----------
#================================

.ONESHELL:
models-BJT: Add_run-dir models-BJT-iv models-BJT-beta

.ONESHELL:
models-BJT-iv: Add_run-dir
	@cp -rf $(Testing_DIR)/regression/bjt_iv  $(Testing_DIR)/$(run_folder)/bjt_iv
	@cd $(Testing_DIR)/$(run_folder)/bjt_iv
	@echo "========== Runing models_ngspice-BJT-IV regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log

# .ONESHELL:
# models-BJT-cv: Add_run-dir
# 	@cp -rf $(Testing_DIR)/regression/bjt_cv  $(Testing_DIR)/$(run_folder)/bjt_cv
# 	@cd $(Testing_DIR)/$(run_folder)/bjt_cv
# 	@echo "========== Runing models_ngspice-BJT-CV regression ==========" |& tee -a ../run_log.log 
# 	@python3 models_regression.py |& tee -a ../run_log.log	

.ONESHELL:
models-BJT-beta: Add_run-dir
	@cp -rf $(Testing_DIR)/regression/bjt_beta  $(Testing_DIR)/$(run_folder)/bjt_beta
	@cd $(Testing_DIR)/$(run_folder)/bjt_beta
	@echo "========== Runing models_ngspice-BJT-BETA regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log

#================================
# --------- models-diode --------
#================================

.ONESHELL:
models-diode: Add_run-dir models-diode-iv

.ONESHELL:
models-diode-iv: Add_run-dir
	@cd $(Testing_DIR)
	@cp -rf $(Testing_DIR)/regression/diode_iv  $(Testing_DIR)/$(run_folder)/diode_iv
	@cd $(Testing_DIR)/$(run_folder)/diode_iv
	@echo "========== Runing models_ngspice-DIODE-IV regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log

# .ONESHELL:
# models-diode-cv: Add_run-dir
# 	@cd $(Testing_DIR)
# 	@cp -rf $(Testing_DIR)/regression/diode_cv  $(Testing_DIR)/$(run_folder)/diode_cv
# 	@cd $(Testing_DIR)/$(run_folder)/diode_cv
# 	@echo "========== Runing models_ngspice-DIODE-CV regression ==========" |& tee -a ../run_log.log 
# 	@python3 models_regression.py |& tee -a ../run_log.log

#================================
# -------- models-MOSCAP --------
#================================

.ONESHELL:
models-CAP-MOS: Add_run-dir models-CAP-MOS-CV

.ONESHELL:
models-CAP-MOS-CV: Add_run-dir
	@cp -rf $(Testing_DIR)/regression/cap_mos_cv  $(Testing_DIR)/$(run_folder)/cap_mos_cv
	@cd $(Testing_DIR)/$(run_folder)/cap_mos_cv
	@echo "========== Runing models_ngspice-CAP-MOS-CV regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log

#================================
# -------- models-MIMCAP --------
#================================

.ONESHELL:
models-CAP-MIM: Add_run-dir models-CAP-MIM-CV

.ONESHELL:
models-CAP-MIM-CV: Add_run-dir
	@cd $(Testing_DIR)
	@cp -rf $(Testing_DIR)/regression/cap_mim_cv  $(Testing_DIR)/$(run_folder)/cap_mim_cv
	@cd $(Testing_DIR)/$(run_folder)/cap_mim_cv
	@echo "========== Runing models_ngspice-CAP-MIM-CV regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log

#================================
# --------- models-RES ----------
#================================

.ONESHELL:
models-RES: Add_run-dir models-RES-R

.ONESHELL:
models-RES-R: Add_run-dir
	@cp -rf $(Testing_DIR)/regression/resistor_r  $(Testing_DIR)/$(run_folder)/resistor_r
	@cd $(Testing_DIR)/$(run_folder)/resistor_r
	@echo "========== Runing models_ngspice-RES-R regression ==========" |& tee -a ../run_log.log 
	@python3 models_regression.py |& tee -a ../run_log.log

#===============================
# --------- Clean ALL ----------
#===============================

.ONESHELL:
clean: 
	@rm -rf $(Testing_DIR)/models_run_*
	@echo "==== Cleaning all old runs is done ===="

#==========================
# --------- HELP ----------
#==========================

# Help Target
help:
	@echo "\n ==== The following are some of the valid targets for this Makefile ====\n"
	@echo "... all                   To run smoke test and regression for all devices"
	@echo "... models-smoke-test     To run smoke test for an inverter     "
	@echo "... models-ngspice        To run regression for all      devices"
	@echo "... models-MOS            To run regression for MOS      devices"
	@echo "... models-BJT            To run regression for BJT      devices"
	@echo "... models-diode          To run regression for diode    devices"
	@echo "... models-CAP-MOS        To run regression for MOSCAP   devices"
	@echo "... models-CAP-MIM        To run regression for MIMCAP   devices"
	@echo "... models-RES            To run regression for RES      devices"
	@echo "... clean                 To clean all old runs"

.PHONY : help
