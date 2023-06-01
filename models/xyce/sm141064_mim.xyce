* ----------------------------------------------------------------------------------------------------
.LIB cap_mim_new
* ----------------------------------------------------------------------------------------------------

* ----------------------------------------------------------------------------------------------------
* OPTION-A [3LM]
* ----------------------------------------------------------------------------------------------------

*/ -------------------------------------------------------------------------------------
*/ MIM Capacitor (1.5fF/um2) subcircuit model for GF's 0.18 Analog CMOS process
*/--------------------------------------------------------------------------------------
.SUBCKT cap_mim_1f5_m2m3_noshield 1 2 PARAMS: C_LENGTH={l} C_WIDTH={w} DTEMP=0 PAR=1
.PARAM
+ C_COX='1.47e-3*mim_corner_1p5fF' C_CAPSW='3.79e-10*mim_corner_1p5fF' C_TNOM=25 C_TC1=4.0604E-05
+ C_TC2=-6.90E-08 C_VCR1=-4.5152E-05 C_VCR2=9.748E-06 C_AREA='c_length*c_width' C_PERI='2*(c_length+c_width)'
+ C_C0='(c_cox*c_area+c_capsw*c_peri)*(1+c_tc1*(temp+dtemp-c_tnom)+c_tc2*(temp+dtemp-c_tnom)*(temp+dtemp-c_tnom))'
*/
*/ model for capacitance
C_cap 1 2 C='c_c0*(1+ c_vcr1*v(1, 2)+c_vcr2*v(1,2)*v(1,2) )*(1+mc_c_cox_1p5fF)'
**
.ENDS cap_mim_1f5_m2m3_noshield

*/ -------------------------------------------------------------------------------------
*/ MIM Capacitor (1fF/um2) subcircuit model for GF's 0.18 Analog CMOS process
*/--------------------------------------------------------------------------------------
.SUBCKT cap_mim_1f0_m2m3_noshield 1 2 PARAMS: C_LENGTH={l} C_WIDTH={w} DTEMP=0 PAR=1
.PARAM
+ C_COX='0.987e-3*mim_corner_1p0fF' C_CAPSW='3.3e-10*mim_corner_1p0fF' C_TNOM=25 C_TC1=1.302e-5
+ C_TC2=-4.93e-9 C_VCR1=6.079e-6 C_VCR2=1.268e-6 C_AREA='c_length*c_width' C_PERI='2*(c_length+c_width)'
+ C_C0='(c_cox*c_area+c_capsw*c_peri)*(1+c_tc1*(temp+dtemp-c_tnom)+c_tc2*(temp+dtemp-c_tnom)*(temp+dtemp-c_tnom))'
*/
*/ model for capacitance
C_cap 1 2 C='c_c0*(1+ c_vcr1*v(1, 2)+c_vcr2*v(1,2)*v(1,2) )*(1+mc_c_cox_1p0fF)'
**
.ENDS cap_mim_1f0_m2m3_noshield

*/ -------------------------------------------------------------------------------------
*/ MIM Capacitor (2fF/um2) subcircuit model for GLOBALFOUNDRIES 0.18 Analog CMOS process M2-M3
*/--------------------------------------------------------------------------------------
.SUBCKT cap_mim_2f0_m2m3_noshield 1 2 PARAMS: C_LENGTH={l} C_WIDTH={w} DTEMP=0 PAR=1
.PARAM GLEAK='9.51e-10/5*10000'
.PARAM C_COX='1.99e-3*mim_corner_2p0fF'
.PARAM C_CAPSW='2.383e-10*mim_corner_2p0fF'
.PARAM
+ C_VCR1='0+(c_width>5u||c_length>5u)*8.742e-6+(c_width<=5u||c_length<=5u)*(-81e-6)'
.PARAM
+ C_VCR2='0+(c_width>5u||c_length>5u)*9.188e-6+(c_width<=5u||c_length<=5u)*(16.7e-6)'
.PARAM C_TNOM=25
.PARAM C_TC1=1.46e-5
.PARAM C_TC2=-5.55e-8
.PARAM C_AREA='c_length*c_width'
.PARAM C_PERI='2*(c_length+c_width)'
.PARAM
+ C_C0='(c_cox*c_AREA+c_capsw*c_PERI)*(1+c_tc1*(temp +dtemp -c_tnom)+c_tc2*(temp+dtemp-c_tnom)*(temp+dtemp-c_tnom))'
*
C_cap 1 2 C='c_c0*(1+c_vcr1*v(1,2)+c_vcr2*v(1,2)*v(1,2))*(1+mc_c_cox_2p0fF)'
R_leak 1 2 R='1/(gleak*c_AREA)' TC1={c_tc1} TC2={c_tc2}
.ENDS cap_mim_2f0_m2m3_noshield

* ----------------------------------------------------------------------------------------------------
* OPTION-B [4LM]
* ----------------------------------------------------------------------------------------------------

*/ -------------------------------------------------------------------------------------
*/ MIM Capacitor (1.5fF/um2) subcircuit model for GF's 0.18 Analog CMOS process
*/--------------------------------------------------------------------------------------
.SUBCKT cap_mim_1f5_m3m4_noshield 1 2 PARAMS: C_LENGTH={l} C_WIDTH={w} DTEMP=0 PAR=1
.PARAM
+ C_COX='1.47e-3*mim_corner_1p5fF' C_CAPSW='3.79e-10*mim_corner_1p5fF' C_TNOM=25 C_TC1=4.0604E-05
+ C_TC2=-6.90E-08 C_VCR1=-4.5152E-05 C_VCR2=9.748E-06 C_AREA='c_length*c_width' C_PERI='2*(c_length+c_width)'
+ C_C0='(c_cox*c_area+c_capsw*c_peri)*(1+c_tc1*(temp+dtemp-c_tnom)+c_tc2*(temp+dtemp-c_tnom)*(temp+dtemp-c_tnom))'
*/
*/ model for capacitance
C_cap 1 2 C='c_c0*(1+ c_vcr1*v(1, 2)+c_vcr2*v(1,2)*v(1,2) )*(1+mc_c_cox_1p5fF)'
**
.ENDS cap_mim_1f5_m3m4_noshield

*/ -------------------------------------------------------------------------------------
*/ MIM Capacitor (1fF/um2) subcircuit model for GF's 0.18 Analog CMOS process
*/--------------------------------------------------------------------------------------
.SUBCKT cap_mim_1f0_m3m4_noshield 1 2 PARAMS: C_LENGTH={l} C_WIDTH={w} DTEMP=0 PAR=1
.PARAM
+ C_COX='0.987e-3*mim_corner_1p0fF' C_CAPSW='3.3e-10*mim_corner_1p0fF' C_TNOM=25 C_TC1=1.302e-5
+ C_TC2=-4.93e-9 C_VCR1=6.079e-6 C_VCR2=1.268e-6 C_AREA='c_length*c_width' C_PERI='2*(c_length+c_width)'
+ C_C0='(c_cox*c_area+c_capsw*c_peri)*(1+c_tc1*(temp+dtemp-c_tnom)+c_tc2*(temp+dtemp-c_tnom)*(temp+dtemp-c_tnom))'
*/
*/ model for capacitance
C_cap 1 2 C='c_c0*(1+ c_vcr1*v(1, 2)+c_vcr2*v(1,2)*v(1,2) )*(1+mc_c_cox_1p0fF)'
**
.ENDS cap_mim_1f0_m3m4_noshield

*/ -------------------------------------------------------------------------------------
*/ MIM Capacitor (2fF/um2) subcircuit model for GLOBALFOUNDRIES 0.18 Analog CMOS process M2-M3
*/--------------------------------------------------------------------------------------
.SUBCKT cap_mim_2f0_m3m4_noshield 1 2 PARAMS: C_LENGTH={l} C_WIDTH={w} DTEMP=0 PAR=1
.PARAM GLEAK='9.51e-10/5*10000'
.PARAM C_COX='1.99e-3*mim_corner_2p0fF'
.PARAM C_CAPSW='2.383e-10*mim_corner_2p0fF'
.PARAM
+ C_VCR1='0+(c_width>5u||c_length>5u)*8.742e-6+(c_width<=5u||c_length<=5u)*(-81e-6)'
.PARAM
+ C_VCR2='0+(c_width>5u||c_length>5u)*9.188e-6+(c_width<=5u||c_length<=5u)*(16.7e-6)'
.PARAM C_TNOM=25
.PARAM C_TC1=1.46e-5
.PARAM C_TC2=-5.55e-8
.PARAM C_AREA='c_length*c_width'
.PARAM C_PERI='2*(c_length+c_width)'
.PARAM
+ C_C0='(c_cox*c_AREA+c_capsw*c_PERI)*(1+c_tc1*(temp +dtemp -c_tnom)+c_tc2*(temp+dtemp-c_tnom)*(temp+dtemp-c_tnom))'
*
C_cap 1 2 C='c_c0*(1+c_vcr1*v(1,2)+c_vcr2*v(1,2)*v(1,2))*(1+mc_c_cox_2p0fF)'
R_leak 1 2 R='1/(gleak*c_AREA)' TC1={c_tc1} TC2={c_tc2}
.ENDS cap_mim_2f0_m3m4_noshield

* ----------------------------------------------------------------------------------------------------
* OPTION-B [5LM]
* ----------------------------------------------------------------------------------------------------

*/ -------------------------------------------------------------------------------------
*/ MIM Capacitor (1.5fF/um2) subcircuit model for GF's 0.18 Analog CMOS process
*/--------------------------------------------------------------------------------------
.SUBCKT cap_mim_1f5_m4m5_noshield 1 2 PARAMS: C_LENGTH={l} C_WIDTH={w} DTEMP=0 PAR=1
.PARAM
+ C_COX='1.47e-3*mim_corner_1p5fF' C_CAPSW='3.79e-10*mim_corner_1p5fF' C_TNOM=25 C_TC1=4.0604E-05
+ C_TC2=-6.90E-08 C_VCR1=-4.5152E-05 C_VCR2=9.748E-06 C_AREA='c_length*c_width' C_PERI='2*(c_length+c_width)'
+ C_C0='(c_cox*c_area+c_capsw*c_peri)*(1+c_tc1*(temp+dtemp-c_tnom)+c_tc2*(temp+dtemp-c_tnom)*(temp+dtemp-c_tnom))'
*/
*/ model for capacitance
C_cap 1 2 C='c_c0*(1+ c_vcr1*v(1, 2)+c_vcr2*v(1,2)*v(1,2) )*(1+mc_c_cox_1p5fF)'
**
.ENDS cap_mim_1f5_m4m5_noshield

*/ -------------------------------------------------------------------------------------
*/ MIM Capacitor (1fF/um2) subcircuit model for GF's 0.18 Analog CMOS process
*/--------------------------------------------------------------------------------------
.SUBCKT cap_mim_1f0_m4m5_noshield 1 2 PARAMS: C_LENGTH={l} C_WIDTH={w} DTEMP=0 PAR=1
.PARAM
+ C_COX='0.987e-3*mim_corner_1p0fF' C_CAPSW='3.3e-10*mim_corner_1p0fF' C_TNOM=25 C_TC1=1.302e-5
+ C_TC2=-4.93e-9 C_VCR1=6.079e-6 C_VCR2=1.268e-6 C_AREA='c_length*c_width' C_PERI='2*(c_length+c_width)'
+ C_C0='(c_cox*c_area+c_capsw*c_peri)*(1+c_tc1*(temp+dtemp-c_tnom)+c_tc2*(temp+dtemp-c_tnom)*(temp+dtemp-c_tnom))'
*/
*/ model for capacitance
C_cap 1 2 C='c_c0*(1+ c_vcr1*v(1, 2)+c_vcr2*v(1,2)*v(1,2) )*(1+mc_c_cox_1p0fF)'
**
.ENDS cap_mim_1f0_m4m5_noshield

*/ -------------------------------------------------------------------------------------
*/ MIM Capacitor (2fF/um2) subcircuit model for GLOBALFOUNDRIES 0.18 Analog CMOS process M2-M3
*/--------------------------------------------------------------------------------------
.SUBCKT cap_mim_2f0_m4m5_noshield 1 2 PARAMS: C_LENGTH={l} C_WIDTH={w} DTEMP=0 PAR=1
.PARAM GLEAK='9.51e-10/5*10000'
.PARAM C_COX='1.99e-3*mim_corner_2p0fF'
.PARAM C_CAPSW='2.383e-10*mim_corner_2p0fF'
.PARAM
+ C_VCR1='0+(c_width>5u||c_length>5u)*8.742e-6+(c_width<=5u||c_length<=5u)*(-81e-6)'
.PARAM
+ C_VCR2='0+(c_width>5u||c_length>5u)*9.188e-6+(c_width<=5u||c_length<=5u)*(16.7e-6)'
.PARAM C_TNOM=25
.PARAM C_TC1=1.46e-5
.PARAM C_TC2=-5.55e-8
.PARAM C_AREA='c_length*c_width'
.PARAM C_PERI='2*(c_length+c_width)'
.PARAM
+ C_C0='(c_cox*c_AREA+c_capsw*c_PERI)*(1+c_tc1*(temp +dtemp -c_tnom)+c_tc2*(temp+dtemp-c_tnom)*(temp+dtemp-c_tnom))'
*
C_cap 1 2 C='c_c0*(1+c_vcr1*v(1,2)+c_vcr2*v(1,2)*v(1,2))*(1+mc_c_cox_2p0fF)'
R_leak 1 2 R='1/(gleak*c_AREA)' TC1={c_tc1} TC2={c_tc2}
.ENDS cap_mim_2f0_m4m5_noshield

* ----------------------------------------------------------------------------------------------------
* OPTION-B [6LM]
* ----------------------------------------------------------------------------------------------------

*/ -------------------------------------------------------------------------------------
*/ MIM Capacitor (1.5fF/um2) subcircuit model for GF's 0.18 Analog CMOS process
*/--------------------------------------------------------------------------------------
.SUBCKT cap_mim_1f5_m5m6_noshield 1 2 PARAMS: C_LENGTH={l} C_WIDTH={w} DTEMP=0 PAR=1
.PARAM
+ C_COX='1.47e-3*mim_corner_1p5fF' C_CAPSW='3.79e-10*mim_corner_1p5fF' C_TNOM=25 C_TC1=4.0604E-05
+ C_TC2=-6.90E-08 C_VCR1=-4.5152E-05 C_VCR2=9.748E-06 C_AREA='c_length*c_width' C_PERI='2*(c_length+c_width)'
+ C_C0='(c_cox*c_area+c_capsw*c_peri)*(1+c_tc1*(temp+dtemp-c_tnom)+c_tc2*(temp+dtemp-c_tnom)*(temp+dtemp-c_tnom))'
*/
*/ model for capacitance
C_cap 1 2 C='c_c0*(1+ c_vcr1*v(1, 2)+c_vcr2*v(1,2)*v(1,2) )*(1+mc_c_cox_1p5fF)'
**
.ENDS cap_mim_1f5_m5m6_noshield

*/ -------------------------------------------------------------------------------------
*/ MIM Capacitor (1fF/um2) subcircuit model for GF's 0.18 Analog CMOS process
*/--------------------------------------------------------------------------------------
.SUBCKT cap_mim_1f0_m5m6_noshield 1 2 PARAMS: C_LENGTH={l} C_WIDTH={w} DTEMP=0 PAR=1
.PARAM
+ C_COX='0.987e-3*mim_corner_1p0fF' C_CAPSW='3.3e-10*mim_corner_1p0fF' C_TNOM=25 C_TC1=1.302e-5
+ C_TC2=-4.93e-9 C_VCR1=6.079e-6 C_VCR2=1.268e-6 C_AREA='c_length*c_width' C_PERI='2*(c_length+c_width)'
+ C_C0='(c_cox*c_area+c_capsw*c_peri)*(1+c_tc1*(temp+dtemp-c_tnom)+c_tc2*(temp+dtemp-c_tnom)*(temp+dtemp-c_tnom))'
*/
*/ model for capacitance
C_cap 1 2 C='c_c0*(1+ c_vcr1*v(1, 2)+c_vcr2*v(1,2)*v(1,2) )*(1+mc_c_cox_1p0fF)'
**
.ENDS cap_mim_1f0_m5m6_noshield

*/ -------------------------------------------------------------------------------------
*/ MIM Capacitor (2fF/um2) subcircuit model for GLOBALFOUNDRIES 0.18 Analog CMOS process M2-M3
*/--------------------------------------------------------------------------------------
.SUBCKT cap_mim_2f0_m5m6_noshield 1 2 PARAMS: C_LENGTH={l} C_WIDTH={w} DTEMP=0 PAR=1
.PARAM GLEAK='9.51e-10/5*10000'
.PARAM C_COX='1.99e-3*mim_corner_2p0fF'
.PARAM C_CAPSW='2.383e-10*mim_corner_2p0fF'
.PARAM
+ C_VCR1='0+(c_width>5u||c_length>5u)*8.742e-6+(c_width<=5u||c_length<=5u)*(-81e-6)'
.PARAM
+ C_VCR2='0+(c_width>5u||c_length>5u)*9.188e-6+(c_width<=5u||c_length<=5u)*(16.7e-6)'
.PARAM C_TNOM=25
.PARAM C_TC1=1.46e-5
.PARAM C_TC2=-5.55e-8
.PARAM C_AREA='c_length*c_width'
.PARAM C_PERI='2*(c_length+c_width)'
.PARAM
+ C_C0='(c_cox*c_AREA+c_capsw*c_PERI)*(1+c_tc1*(temp +dtemp -c_tnom)+c_tc2*(temp+dtemp-c_tnom)*(temp+dtemp-c_tnom))'
*
C_cap 1 2 C='c_c0*(1+c_vcr1*v(1,2)+c_vcr2*v(1,2)*v(1,2))*(1+mc_c_cox_2p0fF)'
R_leak 1 2 R='1/(gleak*c_AREA)' TC1={c_tc1} TC2={c_tc2}
.ENDS cap_mim_2f0_m5m6_noshield

.ENDL cap_mim_new
* ----------------------------------------------------------------------------------------------------
