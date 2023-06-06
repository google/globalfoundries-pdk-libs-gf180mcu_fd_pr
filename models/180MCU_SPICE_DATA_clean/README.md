# MODELS Data extractor

Explains how to extract measured data for GF180MCU models.

## Folder Structure

```text
📁 180MCU_SPICE_DATA_clean
 ┣ 📜README.md                      This file to document the data extractor for GF180MCU.
 ┗ 📁scripts                        Contains all scripts used for data extraction.
 ┣ 📁gf180mcu_data                  Directory that holds clean data and sweeps used for simulation. 
 ```

## **Prerequisites**
You need the following set of tools installed to be able to exctract GF180MCU data:
- Python 3.6+

## **Usage**

The `convert_foundry_csv.py` script takes your input excel file to extract data from it and generating clean version in proper format with sweep csv file to be used in simulation. 

```bash
    scripts/convert_foundry_csv.py (--help| -h)
    scripts/convert_foundry_csv.py --excel_path=<path> --device_type=<device_type>
```

Example:

```bash
    python3 scripts/convert_foundry_csv.py --excel_path=../180MCU_SPICE_DATA/MOS/nfet_03v3_iv.nl_out.xlsx --device_type=nfet_03v3
```

### Options

- `--help -h`                           Print this help message.

- `--excel_path=<excel_path>`           The input excel file for measured data you need to extract.

- `--device_type=<device_type>`         Name of device need to extracted its data.


## **Data extractor Outputs**

You could find the run results at your run directory, results holds all extracted data fromated in a proper way and sweep data file to be used in simulation.

### Folder Structure of run results

```text
 ┣ 📜 <device_name>_meas.csv
 ┗ 📜 <device_name>_sweeps.csv
 ```

## **Makefile Usage**

Also, you could use Makefile to extract all data for all devices in same group, you could run the following command:


```bash
    make models_ext-<device_group>
```

Example:

```bash
    make models_ext-MOS-iv
```

To check all valid target in Makefile, you could run the following command:

```bash
    make help
```

You could find the run results at `gf180mcu_data/<device_group>`/<device_name>_*.csv`.
