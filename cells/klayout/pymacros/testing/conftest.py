import os
import glob
from subprocess import check_call


def pytest_addoption(parser):
    parser.addoption(
        "--device", action="store", default="fet", help="device under test name"
    )


def pytest_generate_tests(metafunc):
    if "device_name" in metafunc.fixturenames:
        dev = metafunc.config.getoption("device")

        devices = []

        # if dev :
        dir_path = os.path.dirname((os.path.abspath(__file__)))
        list_patt_files = glob.glob(os.path.join(dir_path, "patterns", dev, "*.csv"))

        for file_path in list_patt_files:
            devices.append(file_path.split("/")[-1].split("_patt")[0])

        call_str = f"echo {file_path} > file.txt"
        check_call(call_str, shell=True)

        metafunc.parametrize("device_name", devices)
