# PCell Testing

In this folder, the test scripts uses generated patterns from different PCells in form of csv files and save them into GDS files and then we can run DRC aand LVS on them to make sure they are clean.

## Usage

To generate and test the PCells, you run the following:
```bash
pytest --device=<device_name> pcell_reg_Pytest.py
```

After generating the PCells, you could see the testing results as pass or fail tests in pytest summary report 

To run all pcells tests, you need to run the following command :
```bash
make all
```


