# Globalfoundries 180nm MCU models-xyce smoke test

This directory is to test a simple inverter design that simulates with different combinations of sizes, temperature and corners to make sure that device could work with process variations.

## Folder Structure

```text
📁smoke_test
 ┣ 📜README.md                                  This file to document GF180MCU xyce-models smoke test.
 ┣ 📜inv_xyce.spice                             Template for spice netlist used in smoke test.
 ┣ 📜xyce_smoke_test.py                         Main script used for inverter smoke test.
 ```

## Usage

- To test the simple inverter for xyce smoke test, you could use the following command in the current directory:

```bash
python3 📜xyce_smoke_test.py
```

## Smoke test Outputs

You could find the smoke test run results at `run_smoke_<date>_<time>` in the current directory.

### Folder Structure of Smoke test results

```text
📁 run_smoke_<date>_<time>
 ┣ 📜 final_results.csv                  Summary of all combinations used for inverter test.
 ┗ 📁 <device_group>                     Directory for each device group contains all regression results.
    ┣ 📁 netlists                        Contains spice netlists and run logs of smoke test.
    ┣ 📁 simulation                      Generated results for each combination run of xyce smoke test.
 ```
 