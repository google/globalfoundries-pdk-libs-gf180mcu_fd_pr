# Globalfoundries 180nm MCU DRC Testing

Explains how to test GF180nm DRC rule deck.

## Folder Structure

```text
📦testing
 ┣ 📜Makefile
 ┣ 📜README.md
 ┣ 📜run_regression.py
 ┣ 📜run_sc_regression.py
 ┣ 📜sc_testcases
 ┣ 📜switch_checking
 ┗ 📜testcases
 ```

## Prerequisites
You need the following set of tools installed to be able to run the regression:
- Python 3.6+
- KLayout 0.27.8+

We have tested this using the following setup:
- Python 3.9.12
- KLayout 0.27.11

Please make sure to install python packages before running regerssion using the requirements:
```bash
pip install -r ../../requirements.test.txt
```

## Regression Usage

- To make a full test for GF180nm DRC rule deck, you could use the following command in testing directory:

```bash
make all
```

- You could also check allowed targets in the Makefile, using the following command:

    ```bash
    make help
    ```

## **Regression Outputs**

- The resulting files are in one directory with name of `run_<date>_<time>_<rule_deck>` that contains:

    1. A database of all violations.
    2. A CSV report file of total violations and its type (false positive or false negative), and its testing status.
    3. A final CSV report file which indicates the final status of each rule.

- The final report for rules DRC-regression will be generated in the current directory with the name of  `final_report.csv`, also you could find the detailed one with the name of `final_detailed_report.csv`.

- The final report for standard cells DRC-regression will be generated in the current directory with the name of `sc_drc_report.csv`.
