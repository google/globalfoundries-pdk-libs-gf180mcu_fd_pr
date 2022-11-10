# Globalfoundries 180nm MCU models-ngspice regression

Explains how to run GF180nm models-ngspice regression.

## Folder Structure

```text
📦testing
 ┣ 📜Makefile
 ┣ 📜README.md
 ┣ 📦regression
 ┣ 📦smoke_test
 ┣ 📦180MCU_SPICE_Models
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
