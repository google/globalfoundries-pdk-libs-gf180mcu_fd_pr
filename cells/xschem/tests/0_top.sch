v {xschem version=3.1.0 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
L 4 1830 -410 3260 -410 {}
L 4 1830 -650 3260 -650 {}
L 4 1830 -890 3260 -890 {}
L 4 1830 -1130 3260 -1130 {}
L 4 1830 -1250 3260 -1250 {}
L 4 1830 -1370 3260 -1370 {}
L 4 1830 -1490 3260 -1490 {}
L 4 1830 -1610 3260 -1610 {}
L 4 1830 -50 3260 -50 {}
L 7 360 -1330 360 -60 {}
L 7 700 -1330 700 -60 {}
L 7 1040 -1330 1040 -60 {}
L 7 1380 -1330 1380 -60 {}
L 7 1720 -1330 1720 -60 {}
L 7 20 -1330 20 -60 {}
T {MOSFETS} 40 -1310 0 0 0.8 0.8 {}
T {CAPACITORS} 380 -1310 0 0 0.8 0.8 {}
T {BJTs} 730 -1310 0 0 0.8 0.8 {}
T {DIODES} 1060 -1310 0 0 0.8 0.8 {}
T {RESISTORS} 1410 -1310 0 0 0.8 0.8 {}
T {No spice model} 1590 -765 0 0 0.2 0.2 {layer=7}
T {No spice model} 1590 -715 0 0 0.2 0.2 {layer=7}
T {DIODES} 2110 -1570 0 1 0.8 0.8 {}
T {NPNS} 2110 -1450 0 1 0.8 0.8 {}
T {PNPS} 2110 -1330 0 1 0.8 0.8 {}
T {MIMCAPS} 2110 -1210 0 1 0.8 0.8 {}
T {MOSCAPS} 2110 -1040 0 1 0.8 0.8 {}
T {MOSFETS} 2110 -800 0 1 0.8 0.8 {}
T {ESD MOSFETS} 2110 -550 0 1 0.8 0.8 {}
T {RESISTORS} 2110 -250 0 1 0.8 0.8 {}
T {PRIORITY-0 180MCU devices} 660 -1760 0 0 2 2 {}
C {tests/test_nmos_3p3.sym} 190 -310 0 0 {name=x1}
C {tests/test_nmos_3p3_sab.sym} 190 -460 0 0 {name=x2}
C {tests/test_pmos_3p3.sym} 190 -260 0 0 {name=x3}
C {tests/test_pmos_3p3_sab.sym} 190 -510 0 0 {name=x4}
C {devices/title.sym} 160 -30 0 0 {name=l5 author="GlobalFoundries PDK Authors"}
C {devices/launcher.sym} 90 -1440 0 0 {name=h1
descr="List of devices (Google docs)"
url="https://docs.google.com/spreadsheets/d/1xxxg_VzZWJ1NNysSMcOVzyUin7M2dvtb_E7X-5WQKJ0/edit#gid=1056368354"}
C {tests/test_nmos_6p0.sym} 190 -210 0 0 {name=x5}
C {tests/test_pmos_6p0.sym} 190 -160 0 0 {name=x6}
C {tests/test_nmos_6p0_nat.sym} 190 -110 0 0 {name=x7}
C {tests/test_nplus_u.sym} 1550 -1060 0 0 {name=x8}
C {devices/launcher.sym} 90 -1390 0 0 {name=h2
descr="Github"
url="https://github.com/google/gf180mcu-pdk"}
C {tests/test_pmoscap_3p3.sym} 530 -210 0 0 {name=x10}
C {tests/test_pplus_u.sym} 1550 -1010 0 0 {name=x11}
C {tests/test_vnpn_10x10.sym} 870 -110 0 0 {name=x12}
C {tests/test_vpnp_10x10.sym} 870 -460 0 0 {name=x13}
C {tests/test_np_3p3.sym} 1210 -110 0 0 {name=x14}
C {tests/test_nwell.sym} 1550 -110 0 0 {name=x15}
C {tests/test_npolyf_u.sym} 1550 -260 0 0 {name=x16}
C {tests/test_ppolyf_u.sym} 1550 -210 0 0 {name=x17}
C {tests/test_nmoscap_6p0.sym} 530 -110 0 0 {name=x18}
C {tests/test_nmoscap_3p3.sym} 530 -260 0 0 {name=x19}
C {tests/test_pmoscap_6p0.sym} 530 -160 0 0 {name=x20}
C {tests/test_dnwpw.sym} 1210 -160 0 0 {name=x21}
C {tests/test_rm1.sym} 1550 -560 0 0 {name=x22}
C {tests/test_mim_2p0fF.sym} 530 -460 0 0 {name=x23}
C {tests/test_nmos_6p0_sab.sym} 190 -560 0 0 {name=x24}
C {tests/test_pmos_6p0_sab.sym} 190 -610 0 0 {name=x25}
C {tests/test_vpnp_5x5.sym} 870 -510 0 0 {name=x26}
C {tests/test_vnpn_5x5.sym} 870 -160 0 0 {name=x27}
C {tests/test_vnpn_0p54x16.sym} 870 -210 0 0 {name=x28}
C {tests/test_vpnp_0p42x10.sym} 870 -560 0 0 {name=x29}
C {tests/test_vnpn_0p54x8.sym} 870 -260 0 0 {name=x30}
C {tests/test_vnpn_0p54x4.sym} 870 -310 0 0 {name=x31}
C {tests/test_vnpn_0p54x2.sym} 870 -360 0 0 {name=x32}
C {tests/test_vpnp_0p42x5.sym} 870 -610 0 0 {name=x33}
C {tests/test_nplus_s.sym} 1550 -1110 0 0 {name=x34}
C {tests/test_pplus_s.sym} 1550 -1160 0 0 {name=x35}
C {tests/test_npolyf_s.sym} 1550 -360 0 0 {name=x36}
C {tests/test_ppolyf_s.sym} 1550 -310 0 0 {name=x37}
C {tests/test_ppolyf_u_1k.sym} 1550 -410 0 0 {name=x38}
C {tests/test_rm2.sym} 1550 -610 0 0 {name=x39}
C {tests/test_rm3.sym} 1550 -660 0 0 {name=x40}
C {tests/test_rm4.sym} 1550 -710 0 0 {name=x41}
C {tests/test_rm5.sym} 1550 -760 0 0 {name=x42}
C {tests/test_pn_3p3.sym} 1210 -210 0 0 {name=x43}
C {tests/test_np_6p0.sym} 1210 -260 0 0 {name=x44}
C {tests/test_ppolyf_u_1k_6p0.sym} 1550 -460 0 0 {name=x9}
C {tests/test_tm9k.sym} 1550 -810 0 0 {name=x45}
C {tests/test_tm11k.sym} 1550 -860 0 0 {name=x46}
C {tests/test_tm30k.sym} 1550 -910 0 0 {name=x47}
C {symbols/dnwpw.sym} 2220 -1550 0 0 {name=D1
model=dnwpw
r_w=3u
r_l=3u
m=1}
C {symbols/np_3p3.sym} 2360 -1550 0 0 {name=D2
model=np_3p3
r_w=1u
r_l=1u
m=1}
C {symbols/np_6p0.sym} 2500 -1550 0 0 {name=D3
model=np_6p0
r_w=1u
r_l=1u
m=1}
C {symbols/pn_3p3.sym} 2640 -1550 0 0 {name=D4
model=pn_3p3
r_w=1u
r_l=1u
m=1}
C {symbols/vnpn_0p54x16.sym} 2480 -1430 0 0 {name=Q1
model=vnpn_0p54x16
spiceprefix=X
m=1}
C {symbols/vnpn_0p54x2.sym} 2900 -1430 0 0 {name=Q2
model=vnpn_0p54x2
spiceprefix=X
m=1}
C {symbols/vnpn_0p54x4.sym} 2760 -1430 0 0 {name=Q3
model=vnpn_0p54x4
spiceprefix=X
m=1}
C {symbols/vnpn_0p54x8.sym} 2620 -1430 0 0 {name=Q4
model=vnpn_0p54x8
spiceprefix=X
m=1}
C {symbols/vnpn_10x10.sym} 2340 -1430 0 0 {name=Q5
model=vnpn_10x10
spiceprefix=X
m=1}
C {symbols/vnpn_5x5.sym} 2200 -1430 0 0 {name=Q6
model=vnpn_5x5
spiceprefix=X
m=1}
C {symbols/vpnp_0p42x10.sym} 2480 -1310 0 0 {name=Q7
model=vpnp_0p42x10
spiceprefix=X
m=1}
C {symbols/vpnp_0p42x5.sym} 2620 -1310 0 0 {name=Q8
model=vpnp_0p42x5
spiceprefix=X
m=1}
C {symbols/vpnp_10x10.sym} 2340 -1310 0 0 {name=Q9
model=vpnp_10x10
spiceprefix=X
m=1}
C {symbols/vpnp_5x5.sym} 2200 -1310 0 0 {name=Q10
model=vpnp_5x5
spiceprefix=X
m=1}
C {symbols/nmoscap_3p3.sym} 2220 -1070 0 0 {name=C2
W=10e-6
L=10e-6
model=nmoscap_3p3
spiceprefix=X
m=1}
C {symbols/nmoscap_6p0.sym} 2360 -1070 0 0 {name=C3
W=10e-6
L=10e-6
model=nmoscap_6p0
spiceprefix=X
m=1}
C {symbols/pmoscap_3p3.sym} 2220 -950 0 0 {name=C4
W=10e-6
L=10e-6
model=pmoscap_3p3
spiceprefix=X
m=1}
C {symbols/pmoscap_6p0.sym} 2360 -950 0 0 {name=C5
W=10e-6
L=10e-6
model=pmoscap_6p0
spiceprefix=X
m=1}
C {symbols/nmos_3p3_sab.sym} 2200 -590 0 0 {name=M1
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
C {symbols/nmos_3p3.sym} 2200 -830 0 0 {name=M2
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
model=nmos_3p3
spiceprefix=X
}
C {symbols/nmos_6p0_nat.sym} 2480 -830 0 0 {name=M3
L=1.80u
W=0.80u
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nmos_6p0_nat
spiceprefix=X
}
C {symbols/nmos_6p0_sab.sym} 2340 -590 0 0 {name=M4
L=0.70u
W=0.30u
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nmos_6p0_sab
spiceprefix=X
}
C {symbols/nmos_6p0.sym} 2340 -830 0 0 {name=M5
L=0.70u
W=0.30u
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nmos_6p0
spiceprefix=X
}
C {symbols/pmos_3p3_sab.sym} 2200 -470 0 0 {name=M6
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
model=pmos_3p3_sab
spiceprefix=X
}
C {symbols/pmos_3p3.sym} 2200 -710 0 0 {name=M7
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
model=pmos_3p3
spiceprefix=X
}
C {symbols/pmos_6p0_sab.sym} 2340 -470 0 0 {name=M8
L=0.50u
W=0.30u
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pmos_6p0_sab
spiceprefix=X
}
C {symbols/pmos_6p0.sym} 2340 -710 0 0 {name=M9
L=0.50u
W=0.30u
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pmos_6p0
spiceprefix=X
}
C {symbols/mim_2p0fF.sym} 2220 -1190 0 0 {name=C6
W=10e-6
L=10e-6
model=mim_2p0fF
spiceprefix=X
m=1}
C {symbols/nplus_s.sym} 2500 -350 0 0 {name=R1
W=5e-6
L=5e-6
model=nplus_s
spiceprefix=X
m=1}
C {symbols/nplus_u.sym} 2220 -350 0 0 {name=R2
W=5e-6
L=5e-6
model=nplus_u
spiceprefix=X
m=1}
C {symbols/npolyf_s.sym} 2500 -230 0 0 {name=R3
W=1e-6
L=1e-6
model=npolyf_s
spiceprefix=X
m=1}
C {symbols/npolyf_u.sym} 2360 -230 0 0 {name=R4
W=1e-6
L=1e-6
model=npolyf_u
spiceprefix=X
m=1}
C {symbols/nwell.sym} 2220 -230 0 0 {name=R5
W=5e-6
L=5e-6
model=nwell
spiceprefix=X
m=1}
C {symbols/pplus_s.sym} 2640 -350 0 0 {name=R6
W=5e-6
L=5e-6
model=pplus_s
spiceprefix=X
m=1}
C {symbols/pplus_u.sym} 2360 -350 0 0 {name=R7
W=5e-6
L=5e-6
model=pplus_u
spiceprefix=X
m=1}
C {symbols/ppolyf_s.sym} 2780 -230 0 0 {name=R8
W=1e-6
L=1e-6
model=ppolyf_s
spiceprefix=X
m=1}
C {symbols/ppolyf_u_1k_6p0.sym} 3060 -230 0 0 {name=R9
W=1e-6
L=1e-6
model=ppolyf_u_1k_6p0
spiceprefix=X
m=1}
C {symbols/ppolyf_u_1k.sym} 2920 -230 0 0 {name=R10
W=1e-6
L=1e-6
model=ppolyf_u_1k
spiceprefix=X
m=1}
C {symbols/ppolyf_u.sym} 2640 -230 0 0 {name=R11
W=1e-6
L=1e-6
model=ppolyf_u
spiceprefix=X
m=1}
C {symbols/rm1.sym} 2220 -110 0 0 {name=R12
W=0.6e-6
L=60e-6
model=rm1
spiceprefix=X
m=1}
C {symbols/rm2.sym} 2360 -110 0 0 {name=R13
W=0.6e-6
L=60e-6
model=rm2
spiceprefix=X
m=1}
C {symbols/rm3.sym} 2500 -110 0 0 {name=R14
W=0.6e-6
L=60e-6
model=rm3
spiceprefix=X
m=1}
C {symbols/rm4.sym} 2640 -110 0 0 {name=R15
W=0.6e-6
L=60e-6
model=rm4
spiceprefix=X
m=1}
C {symbols/rm5.sym} 2780 -110 0 0 {name=R16
W=0.6e-6
L=60e-6
model=rm5
spiceprefix=X
m=1}
C {symbols/tm11k.sym} 2920 -110 0 0 {name=R17
W=2e-6
L=600e-6
model=tm11k
spiceprefix=X
m=1}
C {symbols/tm30k.sym} 3060 -110 0 0 {name=R18
W=2e-6
L=600e-6
model=tm30k
spiceprefix=X
m=1}
C {symbols/tm9k.sym} 3200 -110 0 0 {name=R19
W=2e-6
L=600e-6
model=tm9k
spiceprefix=X
m=1}
