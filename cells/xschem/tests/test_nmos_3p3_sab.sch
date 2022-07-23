v {xschem version=3.0.0 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 580 -540 1170 -80 {flags=graph
y1=-0.00015
y2=2.1e-20
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=u
x1=0
x2=3.3
divx=5
subdivx=1
node=i(vd)
color=4

unitx=1
dataset=-1}
N 50 -410 90 -410 {
lab=G}
N 130 -490 130 -440 {
lab=D}
N 130 -410 230 -410 {
lab=B}
N 130 -380 130 -310 {
lab=S}
C {devices/code_shown.sym} 20 -160 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"}
C {devices/lab_pin.sym} 50 -410 0 0 {name=l1 sig_type=std_logic lab=G}
C {devices/lab_pin.sym} 130 -490 0 0 {name=l2 sig_type=std_logic lab=D}
C {devices/lab_pin.sym} 130 -310 0 0 {name=l3 sig_type=std_logic lab=S}
C {devices/lab_pin.sym} 230 -410 0 1 {name=l4 sig_type=std_logic lab=B}
C {devices/code_shown.sym} 300 -450 0 0 {name=NGSPICE only_toplevel=true
value="
vg g 0 0
vd d 0 0
vs s 0 0
vb b 0 0
.control
save all
dc vd 0 3.3 0.01 vg 0 3.3 0.3
write test_nmos_3p3_sab.raw
.endc
"}
C {devices/title.sym} 160 -30 0 0 {name=l5 author="GlobalFoundries PDK Authors"}
C {symbols/nmos_3p3_sab.sym} 110 -410 0 0 {name=M1
L=0.28u
W=0.22u
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nmos_3p3_sab
spiceprefix=X
}
C {devices/launcher.sym} 185 -635 0 0 {name=h1
descr="Click left mouse button here with control key
pressed to load/unload waveforms in graph."
tclcommand="
xschem raw_read $netlist_dir/[file tail [file rootname [xschem get current_name]]].raw
"
}
