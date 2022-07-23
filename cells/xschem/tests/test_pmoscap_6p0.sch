v {xschem version=3.0.0 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 750 -540 1340 -80 {flags=graph
y1=0
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
m"}
B 2 750 -1000 1340 -540 {flags=graph
y1=0
y2=4e-13
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
node="\\"Capac; i(v1) m deriv() /\\""}
N 230 -470 230 -420 {
lab=VDD}
N 230 -490 230 -470 {
lab=VDD}
N 50 -330 50 -310 {
lab=M}
N 50 -310 230 -310 {
lab=M}
N 50 -430 50 -390 {
lab=IN}
N 50 -490 230 -490 {
lab=VDD}
N 230 -360 230 -310 {
lab=M}
C {devices/code_shown.sym} 30 -200 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/sm141064.ngspice res_typical
.lib $::180MCU_MODELS/sm141064.ngspice moscap_typical
* .lib $::180MCU_MODELS/sm141064.ngspice res_statistical
"}
C {devices/code_shown.sym} 390 -450 0 0 {name=NGSPICE only_toplevel=true
value="
vvdd vdd 0 6.0
.control
save all
tran 0.1n 200n
write test_pmoscap_6p0.raw
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
C {symbols/pmoscap_6p0.sym} 230 -390 0 0 {name=C1
W=10e-6
L=10e-6
model=pmoscap_6p0
spiceprefix=X
m=1}
C {devices/vsource.sym} 50 -460 0 0 {name=V1 value="pwl 0 0 200n 6.0"}
C {devices/res.sym} 50 -360 0 0 {name=R2
value=100k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 50 -410 0 0 {name=l1 sig_type=std_logic lab=IN}
C {devices/vdd.sym} 230 -490 0 0 {name=l3 lab=VDD}
C {devices/lab_pin.sym} 230 -310 0 1 {name=l2 sig_type=std_logic lab=M}
