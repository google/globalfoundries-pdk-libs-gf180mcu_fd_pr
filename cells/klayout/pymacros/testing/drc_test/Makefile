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

all : test-DRC-pcell

test-DRC-pcell: Add_run-dir  test-DRC-bjt  test-DRC-diode  test-DRC-MIM  test-DRC-cap_mos  test-DRC-MOS  test-DRC-RES

#=================================
# --------- RUN FOLDER ----------
#=================================

.ONESHELL:
Add_run-dir:
	@cd $(Testing_DIR)
	@ mkdir -p $(run_folder)/bjt_drc  $(run_folder)/diode_drc  $(run_folder)/cap_mim_drc  $(run_folder)/mosfet_drc  $(run_folder)/cap_mos_drc  $(run_folder)/res_drc


#================================
# ------- CLONING PV REPO -------
#================================

.ONESHELL:
DRC-PV: 
	@cd $(Testing_DIR)
	@rm -rf globalfoundries-pdk-libs-gf180mcu_fd_pv/
	@git clone https://github.com/efabless/globalfoundries-pdk-libs-gf180mcu_fd_pv.git

#=================================
# ---------- test-DRC-BJT --------
#=================================

.ONESHELL:
test-DRC-bjt: Add_run-dir DRC-PV
	@cd $(Testing_DIR)
	@echo "===== test-DRC for BJT pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/bjt_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/bjt_drc/bjt.log
	@mv -f ../testcases/bjt_pcells*.lyrdb $(run_folder)/bjt_drc


#=================================
# -------- test-DRC-diode -------
#=================================

.ONESHELL:
test-DRC-diode: test-DRC-diode_np  test-DRC-diode_pn test-DRC-np_dw_diode  test-DRC-pn_dw_diode  test-DRC-diode_nw2ps  test-DRC-diode_pw2dw  test-DRC-diode_dw2ps  test-DRC-sc_diode

.ONESHELL:
test-DRC-diode_np: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for diode_np pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/diode_np_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/diode_drc/diode_np.log
	@mv -f ../testcases/diode_np_pcells*.lyrdb $(run_folder)/diode_drc


.ONESHELL:
test-DRC-diode_pn: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for diode_pn pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/diode_pn_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/diode_drc/diode_pn.log
	@mv -f ../testcases/diode_pn_pcells*.lyrdb $(run_folder)/diode_drc


.ONESHELL:
test-DRC-np_dw_diode: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for np_dw_diode pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/np_dw_diode_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/diode_drc/np_dw_diode.log
	@mv -f ../testcases/np_dw_diode_pcells*.lyrdb $(run_folder)/diode_drc


.ONESHELL:
test-DRC-pn_dw_diode: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for pn_dw_diode pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pn_dw_diode_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/diode_drc/pn_dw_diode.log
	@mv -f ../testcases/pn_dw_diode_pcells*.lyrdb $(run_folder)/diode_drc


.ONESHELL:
test-DRC-diode_nw2ps: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for diode_nw2ps pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/diode_nw2ps_pcells.gds   --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/diode_drc/diode_nw2ps.log
	@mv -f ../testcases/diode_nw2ps_pcells*.lyrdb $(run_folder)/diode_drc


.ONESHELL:
test-DRC-diode_pw2dw: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for diode_pw2dw pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/diode_pw2dw_pcells.gds --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/diode_drc/diode_pw2dw.log 
	@mv -f ../testcases/diode_pw2dw_pcells*.lyrdb $(run_folder)/diode_drc


.ONESHELL:
test-DRC-diode_dw2ps: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for diode_dw2ps pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/diode_dw2ps_pcells.gds --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/diode_drc/diode_dw2ps.log
	@mv -f ../testcases/diode_dw2ps_pcells*.lyrdb $(run_folder)/diode_drc


.ONESHELL:
test-DRC-sc_diode: 	Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for sc_diode pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/sc_diode_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/diode_drc/sc_diode.log
	@mv -f ../testcases/sc_diode_pcells*.lyrdb $(run_folder)/diode_drc


#=================================
# --------- test-DRC-MIM ---------
#=================================

.ONESHELL:
test-DRC-MIM: test-DRC-MIM-A  test-DRC-MIM-B

.ONESHELL:
test-DRC-MIM-A: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for MIM-A pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/MIM-A_pcells.gds        --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/cap_mim_drc/mim_a_gfA.log
	@mv -f ../testcases/MIM-A_pcells*.lyrdb $(run_folder)/cap_mim_drc


.ONESHELL:
test-DRC-MIM-B: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for MIM-B pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/MIM-B_gfB_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/cap_mim_drc/mim_b_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/MIM-B_gfC_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/cap_mim_drc/mim_b_gfC.log
	@mv -f ../testcases/MIM-B_gfB_pcells*.lyrdb $(run_folder)/cap_mim_drc



#=================================
# --------- test-DRC-MOS ---------
#=================================

.ONESHELL:
test-DRC-MOS: test-DRC-nfet_03v3  test-DRC-nfet_05v0  test-DRC-nfet_06v0  test-DRC-pfet_03v3  test-DRC-pfet_05v0  test-DRC-pfet_06v0 test-DRC-nfet_03v3_dn  test-DRC-nfet_05v0_dn  test-DRC-nfet_06v0_dn  test-DRC-pfet_03v3_dn  test-DRC-pfet_05v0_dn  test-DRC-pfet_06v0_dn test-DRC-nfet_06v0_nvt  test-DRC-nfet_10v0_asym  test-DRC-pfet_10v0_asym


.ONESHELL:
test-DRC-nfet_03v3: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for nfet_03v3 pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_03v3_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_03v3_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_03v3_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_03v3_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_03v3_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_03v3_gfC.log
	@mv -f ../testcases/nfet_03v3_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-nfet_05v0: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for nfet_05v0 pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_05v0_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_05v0_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_05v0_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_05v0_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_05v0_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_05v0_gfC.log
	@mv -f ../testcases/nfet_05v0_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-nfet_06v0: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for nfet_06v0 pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_06v0_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_06v0_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_06v0_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_06v0_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_06v0_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_06v0_gfC.log
	@mv -f ../testcases/nfet_06v0_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-pfet_03v3: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for pfet_03v3 pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_03v3_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_03v3_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_03v3_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_03v3_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_03v3_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_03v3_gfC.log
	@mv -f ../testcases/pfet_03v3_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-pfet_05v0: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for pfet_05v0 pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_05v0_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_05v0_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_05v0_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_05v0_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_05v0_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_05v0_gfC.log
	@mv -f ../testcases/pfet_05v0_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-pfet_06v0: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for pfet_06v0 pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_06v0_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_06v0_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_06v0_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_06v0_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_06v0_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_06v0_gfC.log
	@mv -f ../testcases/pfet_06v0_pcells*.lyrdb $(run_folder)/mosfet_drc

.ONESHELL:
test-DRC-nfet_03v3_dn: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for nfet_03v3_dn pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_03v3_dn_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_03v3_dn_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_03v3_dn_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_03v3_dn_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_03v3_dn_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_03v3_dn_gfC.log
	@mv -f ../testcases/nfet_03v3_dn_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-nfet_05v0_dn: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for nfet_05v0_dn pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_05v0_dn_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_05v0_dn_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_05v0_dn_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_05v0_dn_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_05v0_dn_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_05v0_dn_gfC.log
	@mv -f ../testcases/nfet_05v0_dn_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-nfet_06v0_dn: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for nfet_06v0_dn pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_06v0_dn_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_06v0_dn_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_06v0_dn_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_06v0_dn_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_06v0_dn_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_06v0_dn_gfC.log
	@mv -f ../testcases/nfet_06v0_dn_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-pfet_03v3_dn: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for pfet_03v3_dn pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_03v3_dn_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_03v3_dn_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_03v3_dn_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_03v3_dn_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_03v3_dn_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_03v3_dn_gfC.log
	@mv -f ../testcases/pfet_03v3_dn_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-pfet_05v0_dn: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for pfet_05v0_dn pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_05v0_dn_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_05v0_dn_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_05v0_dn_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_05v0_dn_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_05v0_dn_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_05v0_dn_gfC.log
	@mv -f ../testcases/pfet_05v0_dn_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-pfet_06v0_dn: Add_run-dir	DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for pfet_06v0_dn pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_06v0_dn_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_06v0_dn_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_06v0_dn_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_06v0_dn_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_06v0_dn_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_06v0_dn_gfC.log
	@mv -f ../testcases/pfet_06v0_dn_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-nfet_06v0_nvt: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for nfet_06v0_nvt pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_06v0_nvt_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_06v0_nvt_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_06v0_nvt_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_06v0_nvt_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_06v0_nvt_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_06v0_nvt_gfC.log
	@mv -f ../testcases/nfet_06v0_nvt_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-nfet_10v0_asym: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for nfet_10v0_asym pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_10v0_asym_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_10v0_asym_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_10v0_asym_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_10v0_asym_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nfet_10v0_asym_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/nfet_10v0_asym_gfC.log
	@mv -f ../testcases/nfet_10v0_asym_pcells*.lyrdb $(run_folder)/mosfet_drc


.ONESHELL:
test-DRC-pfet_10v0_asym: Add_run-dir DRC-PV 	
	@cd $(Testing_DIR)
	@echo "===== test-DRC for pfet_10v0_asym pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_10v0_asym_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_10v0_asym_gfA.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_10v0_asym_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_10v0_asym_gfB.log
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pfet_10v0_asym_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/mosfet_drc/pfet_10v0_asym_gfC.log
	@mv -f ../testcases/pfet_10v0_asym_pcells*.lyrdb $(run_folder)/mosfet_drc


#=================================
# ------- test-DRC-cap_mos --------
#=================================

.ONESHELL:
test-DRC-cap_mos: test-DRC-cap_nmos  test-DRC-cap_pmos test-DRC-cap_nmos_dw  test-DRC-cap_pmos_dw  test-DRC-cap_nmos_b  test-DRC-cap_pmos

.ONESHELL:
test-DRC-cap_nmos: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for cap_nmos pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_nmos_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_nmos_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_nmos_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_nmos_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_nmos_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_nmos_gfC.log 
	@mv -f ../testcases/cap_nmos_pcells*.lyrdb $(run_folder)/cap_mos_drc


.ONESHELL:
test-DRC-cap_pmos: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for cap_pmos pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_pmos_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_pmos_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_pmos_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_pmos_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_pmos_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_pmos_gfC.log 
	@mv -f ../testcases/cap_pmos_pcells*.lyrdb $(run_folder)/cap_mos_drc


.ONESHELL:
test-DRC-cap_nmos_dw: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for cap_nmos_dw pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_nmos_dw_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_nmos_dw_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_nmos_dw_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_nmos_dw_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_nmos_dw_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_nmos_dw_gfC.log 
	@mv -f ../testcases/cap_nmos_dw_pcells*.lyrdb $(run_folder)/cap_mos_drc


.ONESHELL:
test-DRC-cap_pmos_dw: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for cap_pmos_dw pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_pmos_dw_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_pmos_dw_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_pmos_dw_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_pmos_dw_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_pmos_dw_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_pmos_dw_gfC.log 
	@mv -f ../testcases/cap_pmos_dw_pcells*.lyrdb $(run_folder)/cap_mos_drc


.ONESHELL:
test-DRC-cap_nmos_b: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for cap_nmos_b pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_nmos_b_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_nmos_b_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_nmos_b_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_nmos_b_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_nmos_b_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_nmos_b_gfC.log 
	@mv -f ../testcases/cap_nmos_b_pcells*.lyrdb $(run_folder)/cap_mos_drc


.ONESHELL:
test-DRC-cap_pmos_b: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for cap_pmos_b pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_pmos_b_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_pmos_b_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_pmos_b_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_pmos_b_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/cap_pmos_b_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/cap_mos_drc/cap_pmos_b_gfC.log 
	@mv -f ../testcases/cap_pmos_b_pcells*.lyrdb $(run_folder)/cap_mos_drc


#=================================
# --------- test-DRC-RES ---------
#=================================

.ONESHELL:
test-DRC-RES: test-DRC-nplus_u_res  test-DRC-nplus_s_res  test-DRC-pplus_u_res  test-DRC-pplus_s_res  test-DRC-npolyf_u_res  test-DRC-npolyf_s_res  test-DRC-ppolyf_u_res \
			  test-DRC-ppolyf_s_res  test-DRC-ppolyf_u_high_Rs_res  test-DRC-nwell_res  test-DRC-pwell_res  test-DRC-metal_res

.ONESHELL:
test-DRC-nplus_u_res: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for nplus_u_res pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nplus_u_resistor_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/nplus_u_res_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nplus_u_resistor_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/nplus_u_res_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nplus_u_resistor_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/nplus_u_res_gfC.log 
	@mv -f ../testcases/nplus_u_resistor_pcells*.lyrdb $(run_folder)/res_drc


.ONESHELL:
test-DRC-nplus_s_res: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for nplus_s_res pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nplus_s_resistor_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/nplus_s_res_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nplus_s_resistor_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/nplus_s_res_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nplus_s_resistor_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/nplus_s_res_gfC.log 
	@mv -f ../testcases/nplus_s_resistor_pcells*.lyrdb $(run_folder)/res_drc


.ONESHELL:
test-DRC-pplus_u_res: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for pplus_u_res pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pplus_u_resistor_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/pplus_u_res_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pplus_u_resistor_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/pplus_u_res_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pplus_u_resistor_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/pplus_u_res_gfC.log 
	@mv -f ../testcases/pplus_u_resistor_pcells*.lyrdb $(run_folder)/res_drc


.ONESHELL:
test-DRC-pplus_s_res: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for pplus_s_res pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pplus_s_resistor_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/pplus_s_res_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pplus_s_resistor_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/pplus_s_res_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pplus_s_resistor_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/pplus_s_res_gfC.log 
	@mv -f ../testcases/pplus_s_resistor_pcells*.lyrdb $(run_folder)/res_drc


.ONESHELL:
test-DRC-npolyf_u_res: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for npolyf_u_res pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/npolyf_u_resistor_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/npolyf_u_res_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/npolyf_u_resistor_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/npolyf_u_res_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/npolyf_u_resistor_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/npolyf_u_res_gfC.log 
	@mv -f ../testcases/npolyf_u_resistor_pcells*.lyrdb $(run_folder)/res_drc


.ONESHELL:
test-DRC-npolyf_s_res: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for npolyf_s_res pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/npolyf_s_resistor_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/npolyf_s_res_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/npolyf_s_resistor_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/npolyf_s_res_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/npolyf_s_resistor_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/npolyf_s_res_gfC.log 
	@mv -f ../testcases/npolyf_s_resistor_pcells*.lyrdb $(run_folder)/res_drc


.ONESHELL:
test-DRC-ppolyf_u_res: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for ppolyf_u_res pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/ppolyf_u_resistor_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/ppolyf_u_res_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/ppolyf_u_resistor_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/ppolyf_u_res_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/ppolyf_u_resistor_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/ppolyf_u_res_gfC.log 
	@mv -f ../testcases/ppolyf_u_resistor_pcells*.lyrdb $(run_folder)/res_drc


.ONESHELL:
test-DRC-ppolyf_s_res: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for ppolyf_s_res pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/ppolyf_s_resistor_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/ppolyf_s_res_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/ppolyf_s_resistor_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/ppolyf_s_res_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/ppolyf_s_resistor_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/ppolyf_s_res_gfC.log 
	@mv -f ../testcases/ppolyf_s_resistor_pcells*.lyrdb $(run_folder)/res_drc


.ONESHELL:
test-DRC-ppolyf_u_high_Rs_res: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for ppolyf_u_high_Rs_res pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/ppolyf_u_high_Rs_resistor_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/ppolyf_u_high_Rs_res_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/ppolyf_u_high_Rs_resistor_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/ppolyf_u_high_Rs_res_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/ppolyf_u_high_Rs_resistor_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/ppolyf_u_high_Rs_res_gfC.log 
	@mv -f ../testcases/ppolyf_u_high_Rs_resistor_pcells*.lyrdb $(run_folder)/res_drc


.ONESHELL:
test-DRC-nwell_res: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for nwell_res pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nwell_resistor_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/nwell_res_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nwell_resistor_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/nwell_res_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/nwell_resistor_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/nwell_res_gfC.log 
	@mv -f ../testcases/nwell_resistor_pcells*.lyrdb $(run_folder)/res_drc


.ONESHELL:
test-DRC-pwell_res: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for pwell_res pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pwell_resistor_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/pwell_res_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pwell_resistor_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/pwell_res_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/pwell_resistor_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/pwell_res_gfC.log 
	@mv -f ../testcases/pwell_resistor_pcells*.lyrdb $(run_folder)/res_drc


.ONESHELL:
test-DRC-metal_res: Add_run-dir DRC-PV 
	@cd $(Testing_DIR)
	@echo "===== test-DRC for metal_res pcells ====="
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/metal_resistor_rm1_pcells.gds      --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/metal_res_rm1_gfC.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/metal_resistor_rm2_3_pcells.gds    --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/metal_res_rm2_3_gfC.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/metal_resistor_tm30k_pcells.gds    --variant=A --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/metal_res_tm30k_gfA.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/metal_resistor_tm11k_pcells.gds    --variant=B --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/metal_res_tm11k_gfB.log 
	@python3 globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc/run_drc.py --path=../testcases/metal_resistor_tm9k_pcells.gds     --variant=C --antenna  --no_offgrid  |& tee $(run_folder)/res_drc/metal_res_tm9k_gfC.log 
	@mv -f ../testcases/metal_resistor_rm1_pcells*.lyrdb $(run_folder)/res_drc
	@mv -f ../testcases/metal_resistor_rm2_3_pcells*.lyrdb $(run_folder)/res_drc
	@mv -f ../testcases/metal_resistor_tm30k_pcells*.lyrdb $(run_folder)/res_drc
	@mv -f ../testcases/metal_resistor_tm11k_pcells*.lyrdb $(run_folder)/res_drc
	@mv -f ../testcases/metal_resistor_tm9k_pcells*.lyrdb $(run_folder)/res_drc


#==========================
# --------- HELP ----------
#==========================

# Help Target
help:
	@echo "\n ==== The following are some of the valid targets for this Makefile ====\n"
	@echo "... all                        (the default if no target is provided             )"
	@echo "... test-DRC-pcell             (To run DRC for on all pcells                     )"
	@echo "... test-DRC-bjt               (To run DRC for on bjt pcells                     )"
	@echo "... test-DRC-diode             (To run DRC for on diode pcells                   )"
	@echo "... test-DRC-MIM               (To run DRC for on MIM pcells                     )"
	@echo "... test-DRC-MOS               (To run DRC for on MOS pcells                     )"
	@echo "... test-DRC-cap_mos           (To run DRC for on cap_mos pcells                 )"
	@echo "... test-DRC-RES               (To run DRC for on RES pcells                     )"

