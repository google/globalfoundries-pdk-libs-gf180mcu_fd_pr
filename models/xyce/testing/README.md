# Globalfoundries 180nm MCU models-xyce regression

Explains how to run GF180nm models-xyce regression.

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

- Git 2.35+
- Python 3.6+
- Xyce 7.5+

## Regression Usage

- To make a full test for GF180nm models-xyce, you could use the following command in testing directory:

    ```bash
    make all
    ```

- You could also check allowed targets in the Makefile, using the following command:

    ```bash
    make help
    ```

## **Regression Outputs**

After running regression, you should find the following in the folder `run_<date>_<time>` under that folder you will find the folder structure:
```text
run_<date_time>/
├── bjt_beta
│   ├── device_netlists                (Template Netlists)
│   └── models_regression.py           (Regression script for device)
│   ├── <dev>_...                      (Output folder after runing with run logs and actual netlists)
├── bjt_cj
│   ├── device_netlists                (Template Netlists)
│   ├── models_regression.py           (Regression script for device)
│   ├── <dev>_...                      (Output folder after runing with run logs and actual netlists)
├── bjt_iv
│   ├── device_netlists                (Template Netlists)
│   └── models_regression.py           (Regression script for device)
│   ├── <dev>_...                      (Output folder after runing with run logs and actual netlists)
├── diode
│   ├── 0_measured_data
│   ├── device_netlists                (Template Netlists)
│   ├── <dev>_...                      (Output folder after runing with run logs and actual netlists)
│   ├── models_regression.py           (Regression script for device)
├── mimcap_c
│   ├── device_netlists                (Template Netlists)
│   └── models_regression.py           (Regression script for device)
│   ├── <dev>_...                      (Output folder after runing with run logs and actual netlists)
├── moscap_c
│   ├── device_netlists                (Template Netlists)
│   └── models_regression.py           (Regression script for device)
│   ├── <dev>_...                      (Output folder after runing with run logs and actual netlists)
├── mos_cv
│   ├── device_netlists                (Template Netlists)
│   └── models_regression.py           (Regression script for device)
│   ├── <dev>_...                      (Output folder after runing with run logs and actual netlists)
├── mos_iv_vbs
│   ├── device_netlists                (Template Netlists)
│   └── models_regression.py           (Regression script for device)
│   ├── <dev>_...                      (Output folder after runing with run logs and actual netlists)
├── mos_iv_vgs
│   ├── device_netlists                (Template Netlists)
│   └── models_regression.py           (Regression script for device)
│   ├── <dev>_...                      (Output folder after runing with run logs and actual netlists)
├── resistor_r
│   ├── device_netlists                (Template Netlists)
│   └── models_regression.py           (Regression script for device)
│   ├── <dev>_...                      (Output folder after runing with run logs and actual netlists)
└── run_log.log                        (Summary of all runs for all devices)
```

It's important to check the `run_log.log` to see the error per device.
