v {xschem version=3.0.0 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 750 -540 1340 -80 {flags=graph
y1=0.00043
y2=3.3
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=2e-07
divx=5
subdivx=1



unitx=1
dataset=-1
color="4 7"
node="in
p"}
B 2 750 -1000 1340 -540 {flags=graph
y1=-2.8e-13
y2=0
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=2e-07
divx=5
subdivx=1



unitx=1
dataset=-1
color=4
node="\\"Capac; i(v1) p deriv() /\\""}
N 230 -470 230 -420 {
lab=P}
N 230 -360 230 -290 {
lab=GND}
N 50 -490 230 -490 {
lab=P}
N 230 -490 230 -470 {
lab=P}
N 50 -330 50 -310 {
lab=GND}
N 50 -310 230 -310 {
lab=GND}
N 50 -430 50 -390 {
lab=IN}
C {devices/code_shown.sym} 30 -200 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/sm141064.ngspice res_typical
.lib $::180MCU_MODELS/sm141064.ngspice moscap_typical
.lib $::180MCU_MODELS/sm141064.ngspice mimcap_typical
* .lib $::180MCU_MODELS/sm141064.ngspice res_statistical
"}
C {devices/code_shown.sym} 390 -450 0 0 {name=NGSPICE only_toplevel=true
value="
.control
save all
tran 0.1n 200n
write test_mim_2p0fF.raw
.endc
"}
C {devices/title.sym} 160 -30 0 0 {name=l5 author="Stefan Schippers"}
C {devices/launcher.sym} 185 -635 0 0 {name=h1 
descr="Click left mouse button here with control key
pressed to load/unload waveforms in graph." 
tclcommand="
xschem raw_read $netlist_dir/[file tail [file rootname [xschem get current_name]]].raw
"
}
C {symbols/mim_2p0fF.sym} 230 -390 0 0 {name=C1
W=10e-6
L=10e-6
model=mim_2p0fF
spiceprefix=X
m=1}
C {devices/vsource.sym} 50 -360 0 0 {name=V1 value="pwl 0 0 200n 3.3"}
C {devices/res.sym} 50 -460 0 0 {name=R2
value=100k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 50 -410 0 0 {name=l1 sig_type=std_logic lab=IN}
C {devices/gnd.sym} 230 -290 0 0 {name=l2 lab=GND}
C {devices/lab_pin.sym} 230 -490 0 1 {name=l3 sig_type=std_logic lab=P}
