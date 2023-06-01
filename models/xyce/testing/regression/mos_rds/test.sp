* Circuit to measure current versus voltage

* Resistor
R1 1 2 10

* Voltage source
V1 1 0 10

* Current measurement
.DC v1 0 3 0.1

* .MEASURE DC I_R1 DERIV I(R1)
.MEASURE DC I_R1 DERIV I(R1) FROM=0 TO=10

* Print results
.PRINT DC V(1) V(2) I(R1)
