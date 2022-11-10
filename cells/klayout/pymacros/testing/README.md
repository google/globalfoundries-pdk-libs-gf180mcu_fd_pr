# PCell Testing

In this folder, the test scripts generates patterns from different PCells and save them into GDS files and then we can run DRC on them to make sure they are clean.

## Usage

To generate the PCells for testing, you run the following:
```bash
python generate_pcell.py --device=<device_name>
```

To show how to use the `generate_pcell.py` utility:
```bash
python generate_pcell.py -h
```

After generating the PCells, you could run DRC on those cells using the make file in `drc_test`. 

To run all DRC tests, you need to run the following command inside `drc_test` folder:
```bash
make all
```


