# Globalfoundries 180nm MCU models-xyce Standard cells regression

This folder contains simple functionality test for some `gf180mcu_fd_sc` cells.

## Folder Structure

```text
📁sc_regression
 ┣ 📜README.md                                  This file to document GF180MCU xyce-models Standard cells regression.
 ┣ 📁gf180mcu_fd_sc_mcu7t5v0                    Directory for GF180MCU xyce-models Standard cells regression.
    ┣ 📜models_regression.py                    Main regression script used for Models-xyce for mcu7t5v0 std cells.
    ┣ 📁device_netlists                         Contains templates for spice netlists used in std cells regression test.
 ```

## Usage

- To test functionality of some for `gf180mcu_fd_sc_mcu7t5v0` cells, you could use the following command in the current directory:

```bash
cd gf180mcu_fd_sc_mcu7t5v0/
python3 models_regression.py
```

## Standard cells regression Outputs

You could find the results of std cells regression at `run_std_<date>_<time>` in the run directory.

### Folder Structure of Smoke test results

```text
📁 run_std_<date>_<time>
 ┗ 📁 <cell_name>                        Directory for each device group contains all regression results.
    ┣ 📁 inv_measured.csv                Contains actual measured data of some standard cells.
    ┣ 📁 inv_netlists                    Contains spice netlists and run logs of sc regression test.
    ┣ 📁 simulated                       Generated results for each standard cell with different variations.
 ```

