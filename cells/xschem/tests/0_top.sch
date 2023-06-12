v {xschem version=3.1.0 file_version=1.2

* Copyright 2022 GlobalFoundries PDK Authors
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     https://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.

}
G {}
K {}
V {}
S {}
E {}
L 7 360 -730 360 -60 {}
L 7 700 -730 700 -60 {}
L 7 1040 -730 1040 -60 {}
L 7 1380 -730 1380 -60 {}
L 7 1720 -730 1720 -60 {}
L 7 20 -730 20 -60 {}
T {MOSFETS} 40 -710 0 0 0.8 0.8 {}
T {CAPACITORS} 380 -710 0 0 0.8 0.8 {}
T {BJTs} 730 -710 0 0 0.8 0.8 {}
T {DIODES} 1060 -710 0 0 0.8 0.8 {}
T {RESISTORS} 1410 -710 0 0 0.8 0.8 {}
C {test_nfet_03v3.sym} 190 -460 0 0 {name=x1}
C {test_nfet_03v3_dss.sym} 190 -410 0 0 {name=x2}
C {test_pfet_03v3.sym} 190 -360 0 0 {name=x3}
C {test_pfet_03v3_dss.sym} 190 -310 0 0 {name=x4}
C {devices/title.sym} 160 -30 0 0 {name=l5 author="GlobalFoundries PDK Authors"}
C {devices/launcher.sym} 90 -840 0 0 {name=h1
descr="List of devices (Google docs)"
url="https://docs.google.com/spreadsheets/d/1xxxg_VzZWJ1NNysSMcOVzyUin7M2dvtb_E7X-5WQKJ0/edit#gid=1056368354"}
C {test_nfet_06v0.sym} 190 -260 0 0 {name=x5}
C {test_pfet_06v0.sym} 190 -160 0 0 {name=x6}
C {test_nfet_06v0_nvt.sym} 190 -110 0 0 {name=x7}
C {test_nplus_u.sym} 1550 -360 0 0 {name=x8}
C {devices/launcher.sym} 90 -790 0 0 {name=h2
descr="Gitlab"
url="https://gitlab.com"}
C {test_cap_nmos_03v3.sym} 530 -260 0 0 {name=x9}
C {test_cap_pmos_03v3.sym} 530 -210 0 0 {name=x10}
C {test_pplus_u.sym} 1550 -310 0 0 {name=x11}
C {test_npn_10p00x10p00.sym} 870 -110 0 0 {name=x12}
C {test_pnp_10p00x10p00.sym} 870 -160 0 0 {name=x13}
C {test_diode_nd2ps_03v3.sym} 1210 -110 0 0 {name=x14}
C {test_nwell.sym} 1550 -110 0 0 {name=x15}
C {test_npolyf_u.sym} 1550 -210 0 0 {name=x16}
C {test_ppolyf_u.sym} 1550 -160 0 0 {name=x17}
C {test_cap_nmos_06v0.sym} 530 -110 0 0 {name=x18}
C {test_cap_pmos_06v0.sym} 530 -160 0 0 {name=x20}
C {test_diode_pw2dw.sym} 1210 -160 0 0 {name=x21}
C {test_rm1.sym} 1550 -260 0 0 {name=x22}
C {test_cap_mim_2f0fF.sym} 530 -310 0 0 {name=x23}
C {test_nfet_05v0.sym} 190 -210 0 0 {name=x19}
