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
B 2 750 -540 1340 -80 {flags=graph
y1=-0.00049
y2=-1.3e-10
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=u
x1=0.4
x2=0.8
divx=5
subdivx=1



unitx=1
dataset=-1

color=4
node=i(vc)}
B 2 750 -1000 1340 -540 {flags=graph
y1=2.9
y2=11
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0.4
x2=0.8
divx=5
subdivx=1



unitx=1
dataset=-1

color=4
node="\\"Current_gain;i(vc) i(vb) /\\""}
N 210 -390 210 -300 {
lab=GND}
N 130 -390 170 -390 {
lab=B}
N 210 -460 210 -420 {
lab=C}
C {devices/code_shown.sym} 30 -200 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/sm141064.ngspice res_typical
.lib $::180MCU_MODELS/sm141064.ngspice moscap_typical
.lib $::180MCU_MODELS/sm141064.ngspice bjt_typical
* .lib $::180MCU_MODELS/sm141064.ngspice res_statistical
"}
C {devices/code_shown.sym} 390 -450 0 0 {name=NGSPICE only_toplevel=true
value="
vc c 0 dc 3.3
vb b 0 0

.control
dc vb 0.4 0.8 0.001
save all
write test_npn_10p00x10p00.raw
.endc
"}
C {devices/title.sym} 160 -30 0 0 {name=l5 author="GlobalFoundries PDK Authors"}
C {devices/launcher.sym} 185 -635 0 0 {name=h1
descr="Click left mouse button here with control key
pressed to load/unload waveforms in graph."
tclcommand="
xschem raw_read $netlist_dir/[file tail [file rootname [xschem get current_name]]].raw
"
}
C {symbols/npn_10p00x10p00.sym} 190 -390 0 0 {name=Q1
model=npn_10p00x10p00
spiceprefix=X
m=1}
C {devices/gnd.sym} 210 -300 0 0 {name=l1 lab=GND}
C {devices/lab_pin.sym} 130 -390 0 0 {name=l2 sig_type=std_logic lab=B}
C {devices/lab_pin.sym} 210 -460 0 0 {name=l3 sig_type=std_logic lab=C}
