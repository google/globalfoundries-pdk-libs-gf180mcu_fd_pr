# Klayout PCells implementation.

You could use those PCells either in 2 ways:
1. Use volare built PDK directly from: https://github.com/efabless/volare
2. Use the PDK from this primitive library for testing purposes.

## Using PCells from Volare
Please refer to Volare documentation at: https://github.com/efabless/volare/blob/main/Readme.md

## Using PCells from this repo directly.
To use the PDK from this repo directly, you need to do the following:
1. Go to following folder in the repo `cells/klayout` and then run the following command:
```bash
export KLAYOUT_HOME=`pwd`
```
2.(optional step to enable GUI menu for running DRC/LVS) You will need to run the following commands as well from inside `cells/klayout` folder:
```bash
ln -s ../../tech/klayout/gf180mcu.lyt
ln -s ../../tech/klayout/gf180mcu.lyp
```
3. Go to any location where you want to start designing, and open klayout using the following command:
```bash
klayout -e
```
4. Create a new layout for testing.
5. Press on insert instance.
6. Go to the instance menu and select "GF180MCU" library from the library list.
7. Select the search botton and it will give the list of PCells that is available in the library.
8. Select any cell and it will show the cell.
9. Go to the PCell tap and change the parameters as needed to change the layout of the PCells.



