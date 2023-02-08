"""
Globalfoundries 180u lvs test.

Usage:
    pcells_lvs_regression.py (--help| -h)
    pcells_lvs_regression.py (--device=<device_name>) [--thr=<thr>]

Options:
    --help -h                   Print this help message.
    --device=<device_name>      Select your device name.
    --thr=<thr>                 The number of threads used in run.
"""
from docopt import docopt
import os
import sys
from subprocess import check_call
import logging
import glob
import concurrent.futures
import time


def check_klayout_version():
    """
    check_klayout_version checks klayout version and makes sure it would work with the LVS.
    """
    # ======= Checking Klayout version =======
    klayout_v_ = os.popen("klayout -b -v").read()
    klayout_v_ = klayout_v_.split("\n")[0]
    klayout_v_list = []

    if klayout_v_ == "":
        logging.error("Klayout is not found. Please make sure klayout is installed.")
        exit(1)
    else:
        klayout_v_list = [int(v) for v in klayout_v_.split(" ")[-1].split(".")]

    logging.info(f"Your Klayout version is: {klayout_v_}")

    if len(klayout_v_list) < 1 or len(klayout_v_list) > 3:
        logging.error("Was not able to get klayout version properly.")
        exit(1)
    elif len(klayout_v_list) >= 2 or len(klayout_v_list) <= 3:
        if klayout_v_list[1] < 28:
            logging.error("Prerequisites at a minimum: KLayout 0.28.0")
            logging.error(
                "Using this klayout version has not been assesed in this development. Limits are unknown"
            )
            exit(1)


def parse_results_log(results_log):
    """
    This function will parse Klayout log for analysis.
    Parameters
    ----------
    results_log : string or Path object
        Path string to the results file
    Returns
    -------
    int
        An int that contains exit code
    """

    f = open(results_log)
    log_data = f.readlines()
    f.close()
    print(log_data[-2])

    if "ERROR" in log_data[-2]:
        exit_code = 1
    else:
        exit_code = 0

    return exit_code


def run_device(lvs_dir, device_name, test_dir, output_path):
    """
    This function run a single test case using the correct device_name.
    Parameters
    ----------
    lvs_dir : string or Path
        Path to the location where all runsets exist.
    device_name : string
        device name that we are running on.
    test_dir : String
        Path to the location where all runsets exist.
    output_path : String
        Path to the location where all runsets exist.
    Returns
    -------
    tuple
        A tuple with device_name and its exit_code
    """

    print(f"running lvs for {device_name}_pcells")

    pattern_log = f"{output_path}/{device_name}.log"

    call_str = f"""
    python3 {lvs_dir}/run_lvs.py --design={test_dir}/{device_name}.gds --net={device_name}.cdl --gf180mcu="A" > {pattern_log}
    """
    try:
        check_call(call_str, shell=True)
    except Exception:
        pattern_results = glob.glob(os.path.join(test_dir, f"{device_name}.lyrdb"))
        if len(pattern_results) < 1:
            logging.error("generated an exception")
            raise Exception("Failed LVS run.")

    print(f"reading {device_name} log")

    log_res = parse_results_log(f"{pattern_log}")
    res_data = (log_res, device_name)

    return res_data


def run_all_test_cases(device, lvs_dir, test_dir, output_path, num_workers):
    """
    This function run all device test cases from the input list.
    Parameters
    ----------
    device : list
        list that holds all the devices related to device .
    lvs_dir : string or Path
        Path string to the location of the LVS runsets.
    test_dir : String
        Path to the location where all runsets exist.
    output_path : String
        Path to the location where all runsets exist.
    num_workers : int
        Number of workers to use for running the regression.
    Returns
    -------
    tuple
        A pandas DataFrame with all test cases information post running.
    """

    res_data = []
    print(len(device))

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_list = []
        for device_name in device:
            future_list.append(
                executor.submit(
                    run_device, lvs_dir, device_name, test_dir, output_path,
                )
            )

        for future in concurrent.futures.as_completed(future_list):
            try:
                data = future.result()
                res_data.append(data)
            except Exception as exc:
                logging.info(f"Test case generated an exception: {exc}")

    return res_data


def run_regression(device, lvs_dir, test_dir, output_path, cpu_count):
    """
    Running Regression Procedure.
    This function runs the full regression on all test cases.
    Parameters
    ----------
    device : list
        list that holds all the devices related to device .
    lvs_dir : string
        Path string to the LVS directory where LVS_run files are located.
    test_dir : String
        Path to the location where all runsets exist.
    output_path : str
        Path string to the location of the output results of the run.
    cpu_count : int
        Number of cpus to use in running testcases.
    Returns
    -------
    bool
        If all regression passed, it returns true. If any of the rules failed it returns false.
    """

    if "npn" in device:
        devices = ["npn_00p54x02p00"]
    else:
        devices = [device]

    ## Run all devices
    resrults = run_all_test_cases(
        device=devices,
        lvs_dir=lvs_dir,
        test_dir=test_dir,
        output_path=output_path,
        num_workers=cpu_count,
    )
    print(resrults)

    failing_results = []
    for result in resrults:
        if result[0] == 1:
            failing_results.append(f"{result[1]}_pcells")

    if len(failing_results) > 0:
        logging.error("## Some test cases failed .....")
        logging.error(f"Failed Testcases : {failing_results}")
        return False
    else:
        logging.info("## All testcases passed.")
        return True


def main(lvs_dir: str, output_path: str, test_dir: str):
    """
    Main Procedure.
    This function is the main execution procedure
    Parameters
    ----------
    lvs_dir : string
        Path string to the LVS directory where LVS_run files are located.
    test_dir : String
        Path to the location where all runsets exist.
    output_path : str
        Path string to the location of the output results of the run.
    Returns
    -------
    bool
        If all regression passed, it returns true. If any of the rules failed it returns false.
    """

    # Start of execution time
    t0 = time.time()

    ## Check Klayout version
    check_klayout_version()

    # Calling regression function
    run_status = run_regression(
        device=device,
        lvs_dir=lvs_dir,
        test_dir=test_dir,
        output_path=output_path,
        cpu_count=thrCount,
    )

    #  End of execution time
    logging.info("Total execution time {}s".format(time.time() - t0))

    if run_status:
        logging.info("Test completed successfully.")
    else:
        logging.error("Test failed.")
        exit(1)


if __name__ == "__main__":

    # docopt reader
    arguments = docopt(__doc__, version="PCELLS Gen.: 0.1")

    # No. of threads
    thrCount = (
        os.cpu_count() * 2 if arguments["--thr"] is None else int(arguments["--thr"])
    )

    # arguments
    device = arguments["--device"]

    # Paths of regression dirs
    run_lvs_full_path = "../../../../../rules/klayout/lvs"
    test_dir = f"{run_lvs_full_path}/testing/testcases"
    output_path = os.path.join(test_dir, f"{device}_logs")

    # Creating output dir
    os.makedirs(output_path, exist_ok=True)

    # logs format
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler(os.path.join(output_path, "{}.log".format(device))),
            logging.StreamHandler(),
        ],
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Calling main function
    run_status = main(
        lvs_dir=run_lvs_full_path, output_path=output_path, test_dir=test_dir
    )

    # run_regression(device=device,lvs_dir=run_lvs_full_path,test_dir=test_dir,output_path=output_path,cpu_count=thrCount)

    # if "npn" in device:
    #     devices = ["npn_00p54x02p00","rm1"]
    # else:
    #     devices = [device]

    # run_all_test_cases(device=devices,lvs_dir=run_lvs_full_path,test_dir=test_dir,output_path=output_path,num_workers=thrCount)

    # res_data = []

    # for device_name in devices:
    #     res_data.append(run_device(lvs_dir=run_lvs_full_path,device_name=device_name,test_dir=test_dir,output_path=output_path))
    # print(f"running lvs for {device_name}_pcells")

    # call_str = f"""
    # python3 {run_lvs_full_path}/run_lvs.py --design={test_dir}/{device_name}.gds --net={device_name}.cdl --gf180mcu="A" > {output_path}/{device_name}.log
    # """
    # try:
    #     check_call(call_str, shell=True)
    # except Exception :
    #     pattern_results = glob.glob(os.path.join(test_dir, f"{device_name}.lyrdb"))
    #     if len(pattern_results) < 1:
    #         logging.error("generated an exception")
    #         raise Exception("Failed LVS run.")

    # print(f"reading {device_name} log")

    # res_data.append(parse_results_log(f"{output_path}/{device_name}.log"))

    # not_matched = []
    # for dev_res in res_data:
    #     if dev_res[0] == 1:
    #         not_matched.append(f"{dev_res[1]}_pcells")

    # if len(not_matched) > 0:
    #     print(f"not matched pcells : {not_matched}")
    #     exit(1)
