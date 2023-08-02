import pytest
from subprocess import check_call
import os
import yaml


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
    python3 draw_pcell.py --device={device}
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
def test_drc_run(device, device_name):
    """
    run drc testing for device under test testcases

    Args:
        device : name of the device under test
        device_name : name of device testcase to be tested
    """
    # get drc rule_deck path , testing dir path

    file_path = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
    )

    drc_path = "globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/drc"
    drc_dir = os.path.join(root_path, drc_path)

    test_dir = os.path.join(file_path, "testcases")
    patt_dir = os.path.join(file_path, "patterns")
    output_path = os.path.join(test_dir, f"dec_{device}_logs")
    pattern_log = f"{output_path}/{device_name}_drc.log"

    # Creating output dir
    os.makedirs(output_path, exist_ok=True)

    yaml_file = f"{patt_dir}/{device}/{device_name}_patterns.yaml"

    if os.path.isfile(yaml_file):
        with open(yaml_file) as file:
            try:
                var_data = yaml.safe_load(file)
                variant = var_data[device_name]["variant"]
            except yaml.YAMLError as exc:
                print(exc)

        call_str = f"""
        python3 {drc_dir}/run_drc.py --path={test_dir}/{device_name}_pcells.gds --variant={variant} --antenna  --no_offgrid > {pattern_log}
        """

        check = check_call(call_str, shell=True)

    else:

        # run drc command string on vaiants A,B and C
        call_strA = f"""
        python3 {drc_dir}/run_drc.py --path={test_dir}/{device_name}_pcells.gds --variant=A --antenna  --no_offgrid > {pattern_log}
        """

        call_strB = f"""
        python3 {drc_dir}/run_drc.py --path={test_dir}/{device_name}_pcells.gds --variant=B --antenna  --no_offgrid > {pattern_log}
        """

        call_strC = f"""
        python3 {drc_dir}/run_drc.py --path={test_dir}/{device_name}_pcells.gds --variant=C --antenna  --no_offgrid > {pattern_log}
        """

        check = (
            (check_call(call_strA, shell=True)) or check_call(call_strB, shell=True)
        ) or check_call(call_strC, shell=True)

    assert bool(check) == 0


@pytest.mark.dependency(depends=["test_gds_generation", "test_cdl_generation"])
def test_lvs_run(device, device_name):
    """
    run lvs testing for device under test testcases

    Args:
        device : name of the device under test
        device_name : name of device testcase to be tested
    """

    # get lvs rule_deck path , testing dir path
    file_path = os.path.dirname(os.path.abspath(__file__))

    root_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
    )

    lvs_path = "globalfoundries-pdk-libs-gf180mcu_fd_pv/klayout/lvs"
    lvs_dir = os.path.join(root_path, lvs_path)

    test_dir = os.path.join(file_path, "testcases")
    output_path = os.path.join(test_dir, f"lvs_{device}_logs")
    patt_dir = os.path.join(file_path, "patterns")
    pattern_log = f"{output_path}/{device_name}_lvs.log"

    # Creating output dir
    os.makedirs(output_path, exist_ok=True)

    yaml_file = f"{patt_dir}/{device}/{device_name}_patterns.yaml"

    lvs_res = []

    if os.path.isfile(yaml_file):
        with open(yaml_file) as file:
            try:
                var_data = yaml.safe_load(file)
                variant = var_data[device_name]["variant"]
                if variant == "E":
                    variant = "A"
            except yaml.YAMLError as exc:
                print(exc)

        call_str = f"""
    python3 {lvs_dir}/run_lvs.py --layout={test_dir}/{device_name}_pcells.gds --netlist={test_dir}/{device_name}_pcells.cdl --variant={variant} > {pattern_log}
    """

        check_call(call_str, shell=True)

        # read output log of lvs run
        f = open(pattern_log)
        log_data = f.readlines()
        f.close()
        print(log_data[-2])

        if "ERROR" in log_data[-2]:
            lvs_res.append(1)
        else:
            lvs_res.append(0)

    else:

        var_list = ["A", "B", "C"]

        for variant in var_list:

            # run lvs command string
            call_str = f"""
            python3 {lvs_dir}/run_lvs.py --layout={test_dir}/{device_name}_pcells.gds --netlist={test_dir}/{device_name}_pcells.cdl --variant=A > {pattern_log}
            """

            check_call(call_str, shell=True)

            # read output log of lvs run
            f = open(pattern_log)
            log_data = f.readlines()
            f.close()
            print(log_data[-2])

            if "ERROR" in log_data[-2]:
                lvs_res.append(1)
            else:
                lvs_res.append(0)

    if 1 in lvs_res:
        assert False
    else:
        assert True
