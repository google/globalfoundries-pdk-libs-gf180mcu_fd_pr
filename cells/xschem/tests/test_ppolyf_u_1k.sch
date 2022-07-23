v {xschem version=3.1.0 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 580 -540 1170 -80 {flags=graph
y1=-0.0028
y2=0
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=m
x1=0
x2=3.3
divx=5
subdivx=1
node=i(vp)
color=4

unitx=1
dataset=-1}
B 2 580 -1000 1170 -540 {flags=graph
y1=-0
y2=1300
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=3.3
divx=5
subdivx=1



unitx=1
dataset=-1
color=4
node="\\"resistance; p i(vp) / -1 *\\""}
N 130 -490 130 -440 {
lab=P}
N 80 -410 110 -410 {
lab=B}
N 130 -380 130 -310 {
lab=M}
C {devices/code_shown.sym} 20 -160 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/sm141064.ngspice res_typical
* .lib $::180MCU_MODELS/sm141064.ngspice res_statistical
"}
C {devices/lab_pin.sym} 130 -490 0 0 {name=l2 sig_type=std_logic lab=P}
C {devices/lab_pin.sym} 130 -310 0 0 {name=l3 sig_type=std_logic lab=M}
C {devices/lab_pin.sym} 80 -410 0 0 {name=l4 sig_type=std_logic lab=B}
C {devices/code_shown.sym} 300 -450 0 0 {name=NGSPICE only_toplevel=true
value="
vp p 0 0
vm m 0 0
vb b 0 0

.control
save all
dc vp 0 3.3 0.01
write test_ppolyf_u_1k.raw
.endc
"}
C {devices/title.sym} 160 -30 0 0 {name=l5 author="GlobalFoundries PDK Authors"}
C {devices/launcher.sym} 65 -645 0 0 {name=h1
descr="Click left mouse button here with control key
pressed to load/unload waveforms in graph."
tclcommand="
xschem raw_read $netlist_dir/[file tail [file rootname [xschem get current_name]]].raw
"
}
C {symbols/ppolyf_u_1k.sym} 130 -410 0 0 {name=R1
W=1e-6
L=1e-6
model=ppolyf_u_1k
spiceprefix=X
m=1}
