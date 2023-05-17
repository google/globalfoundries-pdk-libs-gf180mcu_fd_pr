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
models_ext-MOS:
	@cd $(Testing_DIR)
	@echo "========== Runing models_ext-MOS ==========" |& tee -a ../run_log.log 
	@python3 convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/nfet_03v3_iv.nl_out.xlsx --device_type=nfet_03v3 |& tee -a ../run_log.log
	@python3 convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/nfet_03v3_dss_iv.nl_out.xlsx --device_type=nfet_03v3_dss |& tee -a ../run_log.log
	@python3 convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/pfet_03v3_iv.nl_out.xlsx --device_type=pfet_03v3 |& tee -a ../run_log.log
	@python3 convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/pfet_03v3_dss_iv.nl_out.xlsx --device_type=pfet_03v3_dss |& tee -a ../run_log.log
	@python3 convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/nfet_06v0_iv.nl_out.xlsx --device_type=nfet_06v0 |& tee -a ../run_log.log
	@python3 convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/nfet_06v0_dss_iv.nl_out.xlsx --device_type=nfet_06v0_dss |& tee -a ../run_log.log
	@python3 convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/nfet_06v0_nvt_iv.nl_out.xlsx --device_type=nfet_06v0_nvt |& tee -a ../run_log.log
	@python3 convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/pfet_06v0_iv.nl_out.xlsx --device_type=pfet_06v0 |& tee -a ../run_log.log
	@python3 convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/pfet_06v0_dss_iv.nl_out.xlsx --device_type=pfet_06v0_dss |& tee -a ../run_log.log
	@rm -rf MOS/ && mkdir -p MOS/
	@mv -f *fet*.csv MOS/

#==========================
# --------- HELP ----------
#==========================

# Help Target
help:
	@echo "\n ==== The following are some of the valid targets for this Makefile ====\n"
	@echo "... all                  (the default if no target is provided  )"
	@echo "... models_ext-MOS       (To extract measured data for MOS devices)"

.PHONY : help
