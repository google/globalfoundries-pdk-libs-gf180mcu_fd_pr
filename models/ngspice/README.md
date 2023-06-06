# GF180MCU ngspice-models

## Folder Structure

```text
📁 ngspice
 ┣ 📜README.md                      This file to document GF180MCU Models for ngspice simulator.
 ┣ 📜design.ngspice                 Global Parameter Settings (MonteCarlo, matching simulation settings, Flicker noise setting).
 ┣ 📜sm141064.ngspice               Model card for all devices except high voltage.
 ┣ 📜sm141064_mim.ngspice           Model card for MIMCAP devices loaded in sm141064.ngspice file.
 ┣ 📜smbb000149.ngspice             High voltage devices model card.
 ┣ 📁testing                        Testing environment directory for GF180MCU ngspice-models.
 ```
