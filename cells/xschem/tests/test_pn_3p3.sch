v {xschem version=3.1.0 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 750 -540 1340 -80 {flags=graph
y1=-3e-05
y2=2.6e-14
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=u
x1=-0.0251239
x2=0.934876
divx=5
subdivx=1



unitx=1
dataset=-1

color=4
node=i(vp)}
N 230 -470 230 -420 {
lab=P}
N 230 -360 230 -290 {
lab=GND}
N 230 -490 230 -470 {
lab=P}
C {devices/code_shown.sym} 30 -200 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/sm141064.ngspice res_typical
.lib $::180MCU_MODELS/sm141064.ngspice moscap_typical
.lib $::180MCU_MODELS/sm141064.ngspice diode_typical
* .lib $::180MCU_MODELS/sm141064.ngspice res_statistical
"}
C {devices/code_shown.sym} 390 -450 0 0 {name=NGSPICE only_toplevel=true
value="
vp p 0 0
.control
save all
dc vp -0.4 0.8 0.001
write test_pn_3p3.raw
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
C {devices/gnd.sym} 230 -290 0 0 {name=l2 lab=GND}
C {devices/lab_pin.sym} 230 -490 0 1 {name=l3 sig_type=std_logic lab=P}
C {symbols/pn_3p3.sym} 230 -390 0 0 {name=D1
model=pn_3p3
r_w=1u
r_l=1u
m=1}
