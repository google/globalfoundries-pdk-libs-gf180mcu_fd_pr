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

At a minimum:

- Git 2.35+
- Python 3.6+
- KLayout 0.27.8+

### On Ubuntu, you can just

`apt install -y build-essential python3`

- Check this [Klayout](https://www.klayout.de/) for klayout installation.

## Regression Usage

To make a full test for GF180nm DRC rule deck, you could use the following command in testing directory:

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
