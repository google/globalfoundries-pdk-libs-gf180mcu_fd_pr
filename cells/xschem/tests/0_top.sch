v {xschem version=3.0.0 file_version=1.2

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
C {gf180mcu_tests/test_nmos_3p3.sym} 190 -410 0 0 {name=x1}
C {gf180mcu_tests/test_nmos_3p3_sab.sym} 190 -360 0 0 {name=x2}
C {gf180mcu_tests/test_pmos_3p3.sym} 190 -310 0 0 {name=x3}
C {gf180mcu_tests/test_pmos_3p3_sab.sym} 190 -260 0 0 {name=x4}
C {devices/title.sym} 160 -30 0 0 {name=l5 author="GlobalFoundries PDK Authors"}
C {devices/launcher.sym} 90 -840 0 0 {name=h1
descr="List of devices (Google docs)"
url="https://docs.google.com/spreadsheets/d/1xxxg_VzZWJ1NNysSMcOVzyUin7M2dvtb_E7X-5WQKJ0/edit#gid=1056368354"}
C {gf180mcu_tests/test_nmos_6p0.sym} 190 -210 0 0 {name=x5}
C {gf180mcu_tests/test_pmos_6p0.sym} 190 -160 0 0 {name=x6}
C {gf180mcu_tests/test_nmos_6p0_nat.sym} 190 -110 0 0 {name=x7}
C {gf180mcu_tests/test_nplus_u.sym} 1550 -360 0 0 {name=x8}
C {devices/launcher.sym} 90 -790 0 0 {name=h2
descr="Gitlab"
url="https://gitlab.com"}
C {gf180mcu_tests/test_nmoscap_3p3.sym} 530 -260 0 0 {name=x9}
C {gf180mcu_tests/test_pmoscap_3p3.sym} 530 -210 0 0 {name=x10}
C {gf180mcu_tests/test_pplus_u.sym} 1550 -310 0 0 {name=x11}
C {gf180mcu_tests/test_vnpn_10x10.sym} 870 -110 0 0 {name=x12}
C {gf180mcu_tests/test_vpnp_10x10.sym} 870 -160 0 0 {name=x13}
C {gf180mcu_tests/test_np_3p3.sym} 1210 -110 0 0 {name=x14}
C {gf180mcu_tests/test_nwell.sym} 1550 -110 0 0 {name=x15}
C {gf180mcu_tests/test_npolyf_u.sym} 1550 -210 0 0 {name=x16}
C {gf180mcu_tests/test_ppolyf_u.sym} 1550 -160 0 0 {name=x17}
C {gf180mcu_tests/test_nmoscap_6p0.sym} 530 -110 0 0 {name=x18}
C {gf180mcu_tests/test_nmoscap_3p3.sym} 530 -260 0 0 {name=x19}
C {gf180mcu_tests/test_pmoscap_6p0.sym} 530 -160 0 0 {name=x20}
C {gf180mcu_tests/test_dnwpw.sym} 1210 -160 0 0 {name=x21}
C {gf180mcu_tests/test_rm1.sym} 1550 -260 0 0 {name=x22}
C {gf180mcu_tests/test_mim_2p0fF.sym} 530 -310 0 0 {name=x23}
