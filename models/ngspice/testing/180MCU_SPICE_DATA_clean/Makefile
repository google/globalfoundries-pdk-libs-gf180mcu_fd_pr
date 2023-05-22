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

#=============================================================
# --------------------- MODELS-EXTRACTOR ---------------------
#=============================================================

SHELL := /bin/bash
Testing_DIR ?= $(shell pwd)

.DEFAULT_GOAL := all

all : models-ngspice smoke-test

models-extract: models_ext-MOS

#================================
# -------- models_ext-MOS--------
#================================

.ONESHELL:
models_ext-MOS-iv:
	@cd $(Testing_DIR)
	@echo "========== Runing models_ext-MOS-iv ==========" |& tee -a ../run_log.log 
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/nfet_03v3_iv.nl_out.xlsx --device_type=nfet_03v3 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/nfet_03v3_dss_iv.nl_out.xlsx --device_type=nfet_03v3_dss |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/pfet_03v3_iv.nl_out.xlsx --device_type=pfet_03v3 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/pfet_03v3_dss_iv.nl_out.xlsx --device_type=pfet_03v3_dss |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/nfet_06v0_iv.nl_out.xlsx --device_type=nfet_06v0 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/nfet_06v0_dss_iv.nl_out.xlsx --device_type=nfet_06v0_dss |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/nfet_06v0_nvt_iv.nl_out.xlsx --device_type=nfet_06v0_nvt |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/pfet_06v0_iv.nl_out.xlsx --device_type=pfet_06v0 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/pfet_06v0_dss_iv.nl_out.xlsx --device_type=pfet_06v0_dss |& tee -a ../run_log.log
	@rm -rf gf180mcu_data/MOS_iv/ && mkdir -p gf180mcu_data/MOS_iv/
	@mv -f *fet*.csv gf180mcu_data/MOS_iv/

.ONESHELL:
models_ext-MOS-cv:
	@cd $(Testing_DIR)
	@echo "========== Runing models_ext-MOS-cv ==========" |& tee -a ../run_log.log 
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/fet_03v3_cv.nl_out.xlsx --device_type=fet_03v3 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/fet_03v3_dss_cv.nl_out.xlsx --device_type=fet_03v3_dss |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/fet_06v0_cv.nl_out.xlsx --device_type=fet_06v0 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/fet_06v0_dss_cv.nl_out.xlsx --device_type=fet_06v0_dss |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/fet_06v0_nvt_cv.nl_out.xlsx --device_type=fet_06v0_nvt |& tee -a ../run_log.log
	@rm -rf gf180mcu_data/MOS_cv/ && mkdir -p gf180mcu_data/MOS_cv/
	@mv -f *fet*.csv gf180mcu_data/MOS_cv/

#===============================
# ------ models_ext-MOSCAP------
#===============================

.ONESHELL:
models_ext-MOSCAP:
	@cd $(Testing_DIR)
	@echo "========== Runing models_ext-MOSCAP ==========" |& tee -a ../run_log.log 
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Cap/moscap_cv_3p3.nl_out.xlsx --device_type=cap_mos_03v3 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Cap/moscap_cv_6p0.nl_out.xlsx --device_type=cap_mos_06v0 |& tee -a ../run_log.log
	@rm -rf gf180mcu_data/MOSCAP_cv/ && mkdir -p gf180mcu_data/MOSCAP_cv/
	@mv -f *cap_mos*.csv gf180mcu_data/MOSCAP_cv/

#==========================
# --------- HELP ----------
#==========================

# Help Target
help:
	@echo "\n ==== The following are some of the valid targets for this Makefile ====\n"
	@echo "... all                  (the default if no target is provided  )"
	@echo "... models_ext-MOS-iv    (To extract measured data for MOS-iv devices)"
	@echo "... models_ext-MOS-cv    (To extract measured data for MOS-cv devices)"
	@echo "... models_ext-MOSCAP    (To extract measured data for MOSCAP devices)"

.PHONY : help
