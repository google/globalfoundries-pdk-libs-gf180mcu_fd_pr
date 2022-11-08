# GDS/TXT Conversion Documentation

Explains how to use the converter.

## Folder Structure

```text
📦gds2txt
 ┣ 📦testing
 ┗ 📜gds_convert.py
 ```

## Pre-requesties

Before using the script, A tool `python-gdsii` must be installed. Simply you can just type:

```bash
    pip install python-gdsii
```

## Explaination

The `gds_convert.py` script takes a gds file and convert it to a text file or bring back a gds file by converting it from a text file.

### **Options**

1. **mode**=to   : takes a gds file and convert it to a text file.
2. **mode**=from : bring back a gds file by converting it from a text file.

## Usage

```bash
    gds_convert.py (--help| -h)
    gds_convert.py (--gds=<layout_path>) (--mode=<mode>) (--txt=<txt_path>)
```

Example:

```bash
    gds_convert.py --gds=and_gate.gds --mode=to --txt=and_gate.txt
```

### Options

`--help -h`                            Print a help message.

`--gds=<gds_path>`                     The input GDS file path.

`--mode=<mode>`                        The operation mode (to, form).

`--txt=<txt_path>`                     The input text file path.
