# Globalfoundries 180nm MCU models-ngspice regression

Explains how to run GF180nm models-ngspice regression.

## Folder Structure

```text
📦testing
 ┣ 📜Makefile                                   (Makefile to setup test cases)
 ┣ 📜README.md                                  (This file)
 ┣ 📦sc_regression/gf180mcu_fd_sc_mcu7t5v0      (Standard cells regression that simulates the standard cells using different voltage stimulus.)
 ┣ 📦regression                                 (This is the regression folder that has a test case per device.)
 ┣ 📦smoke_test                                 (An inverter design that simulates in all corners to make sure that all corners will work with no issue.)
 ┣ 📦180MCU_SPICE_Models                        (Foundry measurement data used for model calibration.)
 ```

## Prerequisites

At a minimum:
- Python 3.6+
- ngspice-37+

Our test environment has the following:
- Python 3.9.12
- ngspice-37

## Regression Usage

- To make a full test for GF180nm models-ngspice, you could use the following command in testing directory:

    ```bash
    make all
    ```

- You could also check allowed targets in the Makefile, using the following command:

    ```bash
    make help
    ```

## **Regression Outputs**

- The resulting files are in `regression/<device_folder>/` with name of `<device_name><options>` that contains:

    1. A final report file of all results.
    2. measured folder that contains measured data used in regression.
    3. simulated folder that contains simulated data used in regression.
    4. netlists folder that contains spice files used in simulation.
