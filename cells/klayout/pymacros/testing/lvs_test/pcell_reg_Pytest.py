import pytest
from subprocess import check_call
import os


@pytest.fixture
def device(request):
    """
    Returns device argument read from command line
    """
    return request.config.getoption("--device")


@pytest.mark.dependency()
def test_gds_generation(device):
    """
    generate gds files for device under test

    Args:
        device : name of the device under test
    """

    # gds generation command string
    call_str = f"""
    python3 ../draw_pcell.py --device={device}
    """

    # assert whether generation is passed
    assert bool(check_call(call_str, shell=True)) == 0


@pytest.mark.dependency()
def test_cdl_generation(device):
    """
    generate cdl files for device under test

    Args:
        device : name of the device under test
    """

    # cdl generation command string
    call_str = f"""
    python3 cdl_gen.py --device={device}
    """

    # assert whether generation is passed
    assert bool(check_call(call_str, shell=True)) == 0


@pytest.mark.dependency(depends=["test_gds_generation"])
def test_drc_run(device):
    """
    run drc testing for device under test testcases

    Args:
        device : name of the device under test
        device_name : name of device testcase to be tested
    """
    device_name = "nfet_temp_pass"
    # get drc rule_deck path , testing dir path

    file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
    )

    drc_path = "rules/klayout/drc"
    drc_dir = os.path.join(root_path, drc_path)

    test_dir = os.path.join(file_path, "testcases")
    output_path = os.path.join(test_dir, f"dec_{device}_logs")
    pattern_log = f"{output_path}/{device_name}_drc.log"

    # Creating output dir
    os.makedirs(output_path, exist_ok=True)

    # run drc command string
    call_str = f"""
    python3 {drc_dir}/run_drc.py --path={test_dir}/{device_name}_pcells.gds --variant="B" > {pattern_log}
    """
    assert bool(check_call(call_str, shell=True)) == 0


@pytest.mark.dependency(depends=["test_gds_generation", "test_cdl_generation"])
def test_lvs_run(device, device_name):
    """
    run lvs testing for device under test testcases

    Args:
        device : name of the device under test
        device_name : name of device testcase to be tested
    """

    # get lvs rule_deck path , testing dir path
    file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
    )

    lvs_path = "rules/klayout/lvs"
    lvs_dir = os.path.join(root_path, lvs_path)

    test_dir = os.path.join(file_path, "testcases")
    output_path = os.path.join(test_dir, f"lvs_{device}_logs")
    pattern_log = f"{output_path}/{device_name}_lvs.log"

    # Creating output dir
    os.makedirs(output_path, exist_ok=True)

    # run lvs command string
    call_str = f"""
    python3 {lvs_dir}/run_lvs.py --design={test_dir}/{device_name}_pcells.gds --net={device_name}_pcells.cdl --gf180mcu="A" > {pattern_log}
    """
    check_call(call_str, shell=True)

    # read output log of lvs run
    f = open(pattern_log)
    log_data = f.readlines()
    f.close()
    print(log_data[-2])

    if "ERROR" in log_data[-2]:
        assert False
    else:
        assert True
