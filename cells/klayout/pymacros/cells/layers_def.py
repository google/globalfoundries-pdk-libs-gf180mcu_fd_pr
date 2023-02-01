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

########################################################################################################################
## layers definition for Klayout of GF180MCU
########################################################################################################################

from gdsfactory.types import LayerSpec


 
comp_layer : LayerSpec = (22,0)
         
dnwell_layer : LayerSpec = (12,0)
         
nwell_layer : LayerSpec = (21,0)
         
lvpwell_layer : LayerSpec = (204,0)
         
dualgate_layer : LayerSpec = (55,0)
         
poly2_layer : LayerSpec = (30,0)
         
nplus_layer : LayerSpec = (32,0)
         
pplus_layer : LayerSpec = (31,0)
         
sab_layer : LayerSpec = (49,0)
         
esd_layer : LayerSpec = (24,0)
         
contact_layer : LayerSpec = (33,0)
         
m1_layer : LayerSpec = (34,0)
         
via1_layer : LayerSpec = (35,0)
         
m2_layer : LayerSpec = (36,0)
         
via2_layer : LayerSpec = (38,0)
         
m3_layer : LayerSpec = (42,0)
         
via3_layer : LayerSpec = (40,0)
         
m4_layer : LayerSpec = (46,0)
         
via4_layer : LayerSpec = (41,0)
         
m5_layer : LayerSpec = (81,0)
         
via5_layer : LayerSpec = (82,0)
         
metaltop_layer : LayerSpec = (53,0)
         
pad_layer : LayerSpec = (37,0)
         
resistor_layer : LayerSpec = (62,0)
         
fhres_layer : LayerSpec = (227,0)
         
fusetop_layer : LayerSpec = (75,0)
         
fusewindow_d_layer : LayerSpec = (96,1)
         
polyfuse_layer : LayerSpec = (220,0)
         
mvsd_layer : LayerSpec = (210,0)
         
mvpsd_layer : LayerSpec = (11,39)
         
nat_layer : LayerSpec = (5,0)
         
comp_dummy_layer : LayerSpec = (22,4)
         
poly2_dummy_layer : LayerSpec = (30,4)
         
metal1_dummy_layer : LayerSpec = (34,4)
         
metal2_dummy_layer : LayerSpec = (36,4)
         
metal3_dummy_layer : LayerSpec = (42,4)
         
metal4_dummy_layer : LayerSpec = (46,4)
         
metal5_dummy_layer : LayerSpec = (81,4)
         
metaltop_dummy_layer : LayerSpec = (53,4)
         
comp_label_layer : LayerSpec = (22,10)
         
poly2_label_layer : LayerSpec = (30,10)
         
metal1_label_layer : LayerSpec = (34,10)
         
metal2_label_layer : LayerSpec = (36,10)

metal3_label_layer : LayerSpec = (42,10)
         
metal4_label_layer : LayerSpec = (46,10)
         
metal5_label_layer : LayerSpec = (81,10)
         
metaltop_label_layer : LayerSpec = (53,10)
         
metal1_slot_layer : LayerSpec = (34,3)
         
metal2_slot_layer : LayerSpec = (36,3)
         
metal3_slot_layer : LayerSpec = (42,3)
         
metal4_slot_layer : LayerSpec = (46,3)
         
metal5_slot_layer : LayerSpec = (81,3)
         
metaltop_slot_layer : LayerSpec = (53,3)
         
ubmpperi_layer : LayerSpec = (183,0)
         
ubmparray_layer : LayerSpec = (184,0)
         
ubmeplate_layer : LayerSpec = (185,0)
         
sc_diode_mk_layer : LayerSpec = (241,0)
         
zener_layer : LayerSpec = (178,0)
         
res_mk_layer : LayerSpec = (110,5)
         
opc_drc_layer : LayerSpec = (124,5)
         
ndmy_layer : LayerSpec = (111,5)
         
pmndmy_layer : LayerSpec = (152,5)
         
v5_xtor_layer : LayerSpec = (112,1)
         
cap_mk_layer : LayerSpec = (117,5)
         
mos_cap_mk_layer : LayerSpec = (166,5)
         
ind_mk_layer : LayerSpec = (151,5)
         
diode_mk_layer : LayerSpec = (115,5)
         
drc_bjt_layer : LayerSpec = (127,5)
         
lvs_bjt_layer : LayerSpec = (118,5)
         
mim_l_mk_layer : LayerSpec = (117,10)
         
latchup_mk_layer : LayerSpec = (137,5)
         
guard_ring_mk_layer : LayerSpec = (167,5)
         
otp_mk_layer : LayerSpec = (173,5)
         
mtpmark_layer : LayerSpec = (122,5)
         
neo_ee_mk_layer : LayerSpec = (88,17)
         
sramcore_layer : LayerSpec = (108,5)
         
lvs_rf_layer : LayerSpec = (100,5)
         
lvs_drain_layer : LayerSpec = (100,7)
         
ind_mk1_layer : LayerSpec = (151,5)
         
hvpolyrs_layer : LayerSpec = (123,5)
         
lvs_io_layer : LayerSpec = (119,5)
         
probe_mk_layer : LayerSpec = (13,17)
         
esd_mk_layer : LayerSpec = (24,5)
         
lvs_source_layer : LayerSpec = (100,8)
         
well_diode_mk_layer : LayerSpec = (153,51)
         
ldmos_xtor_layer : LayerSpec = (226,0)
         
plfuse_layer : LayerSpec = (125,5)
         
efuse_mk_layer : LayerSpec = (80,5)
         
mcell_feol_mk_layer : LayerSpec = (11,17)
         
ymtp_mk_layer : LayerSpec = (86,17)
         
dev_wf_mk_layer : LayerSpec = (128,17)
         
metal1_blk_layer : LayerSpec = (34,5)
         
metal2_blk_layer : LayerSpec = (36,5)
         
metal3_blk_layer : LayerSpec = (42,5)
         
metal4_blk_layer : LayerSpec = (46,5)
         
metal5_blk_layer : LayerSpec = (81,5)
         
metalt_blk_layer : LayerSpec = (53,5)
         
pr_bndry_layer : LayerSpec = (0,0)
         
mdiode_layer : LayerSpec = (116,5)
         
metal1_res_layer : LayerSpec = (110,11)
         
metal2_res_layer : LayerSpec = (110,12)
         
metal3_res_layer : LayerSpec = (110,13)
         
metal4_res_layer : LayerSpec = (110,14)
         
metal5_res_layer : LayerSpec = (110,15)
         
metal6_res_layer : LayerSpec = (110,16)
         
border_layer : LayerSpec = (63,0)
        