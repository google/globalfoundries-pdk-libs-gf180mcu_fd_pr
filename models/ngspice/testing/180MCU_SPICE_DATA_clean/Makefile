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

#===============================
# ------ models_ext-MIMCAP------
#===============================

.ONESHELL:
models_ext-MIMCAP:
	@cd $(Testing_DIR)
	@echo "========== Runing models_ext-MIMCAP ==========" |& tee -a ../run_log.log 
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Cap/mimcap_fc.nl_out.xlsx --device_type=cap_mim |& tee -a ../run_log.log
	@rm -rf gf180mcu_data/MIMCAP_cv/ && mkdir -p gf180mcu_data/MIMCAP_cv/
	@mv -f *cap_mim*.csv gf180mcu_data/MIMCAP_cv/

#===============================
# ------ models_ext-diode ------
#===============================

.ONESHELL:
models_ext-DIODE-iv:
	@cd $(Testing_DIR)
	@echo "========== Runing models_ext-DIODE-iv ==========" |& tee -a ../run_log.log 
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Diode/diode_dw2ps_iv.nl_out.xlsx --device_type=diode_dw2ps |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Diode/diode_nd2ps_03v3_iv.nl_out.xlsx --device_type=diode_nd2ps_03v3 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Diode/diode_nd2ps_06v0_iv.nl_out.xlsx --device_type=diode_nd2ps_06v0 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Diode/diode_nw2ps_03v3_iv.nl_out.xlsx --device_type=diode_nw2ps_03v3 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Diode/diode_nw2ps_06v0_iv.nl_out.xlsx --device_type=diode_nw2ps_06v0 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Diode/diode_pd2nw_03v3_iv.nl_out.xlsx --device_type=diode_pd2nw_03v3 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Diode/diode_pd2nw_06v0_iv.nl_out.xlsx --device_type=diode_pd2nw_06v0 |& tee -a ../run_log.log
	@python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Diode/diode_pw2dw_iv.nl_out.xlsx --device_type=diode_pw2dw |& tee -a ../run_log.log
	@rm -rf gf180mcu_data/diode_iv/ && mkdir -p gf180mcu_data/diode_iv/
	@mv -f *diode*_iv*.csv gf180mcu_data/diode_iv/

#============================
# ------ models_ext-RES------
#============================

res_devices = \
	nplus_u \
	pplus_u \
	nplus_s \
	pplus_s \
	npolyf_u \
	ppolyf_u \
	npolyf_s \
	ppolyf_s \
	ppolyf_u_1k \
	ppolyf_u_2k \
	ppolyf_u_1k_6p0 \
	ppolyf_u_2k_6p0 \
	ppolyf_u_3k \
	rm1 \
	rm2 \
	rm3 \
	tm6k \
	tm9k \
	tm11k \
	tm30k \
	nwell

.ONESHELL:
models_ext-RES:
	@for res in $(res_devices); do \
		python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Resistor/RES*a-wl-$$res.nl_out.xlsx --device_type=$$res |& tee -a ../run_log.log ; \
		python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/Resistor/RES*b-temp-$$res.nl_out.xlsx --device_type=$$res |& tee -a ../run_log.log ; \
	done
	@rm -rf gf180mcu_data/RES_r/ && mkdir -p gf180mcu_data/RES_r/
	@mv -f *res*.csv gf180mcu_data/RES_r/


#==========================
# --------- HELP ----------
#==========================

help:
	@echo "\n ==== The following are some of the valid targets for this Makefile ====\n"
	@echo "... all                  (the default if no target is provided  )"
	@echo "... models_ext-MOS-iv    (To extract measured data for MOS-iv devices)"
	@echo "... models_ext-MOS-cv    (To extract measured data for MOS-cv devices)"
	@echo "... models_ext-MOSCAP    (To extract measured data for MOSCAP devices)"
	@echo "... models_ext-MIMCAP    (To extract measured data for MIMCAP devices)"
<<<<<<< HEAD
	@echo "... models_ext-DIODE-iv  (To extract measured data for MIMCAP devices)"
=======
	@echo "... models_ext-RES       (To extract measured data for RES devices)"
>>>>>>> bfbad8216b0d80f01ae6d42af7c136598b2cceb6

.PHONY : help
