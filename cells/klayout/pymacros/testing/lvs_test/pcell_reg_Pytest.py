import pytest
from subprocess import check_call
import os
import glob
import logging


@pytest.mark.dependency()
def test_gds_generation():

    call_str = f"""
    python3 ../draw_pcell.py --device=fet
    """
    assert bool(check_call(call_str, shell=True)) == 0


@pytest.mark.dependency()
def test_cdl_generation():

    call_str = f"""
    python3 cdl_gen.py --device=fet
    """
    assert bool(check_call(call_str, shell=True)) == 0


def get_devices_list(target_device):

    file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    list_patt_files = glob.glob(
        os.path.join(file_path, "patterns", target_device, "*.csv")
    )

    devices = []
    for file_path in list_patt_files:
        devices.append(file_path.split("/")[-1].split("_patt")[0])

    return devices

@pytest.mark.parametrize("device_name", get_devices_list("fet"))

@pytest.mark.dependency(depends=["test_gds_generation"])
def test_drc_run(device_name):

    file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    file_path
                )
            )
        )
    )
    
    drc_path = "rules/klayout/drc"
    drc_dir = os.path.join(root_path, drc_path)

    test_dir = os.path.join(file_path, "testcases")
    output_path = os.path.join(test_dir, f"fet_logs")
    pattern_log = f"{output_path}/{device_name}_drc.log"
    
    # Creating output dir
    os.makedirs(output_path, exist_ok=True)

    call_str = f"""
    python3 {drc_dir}/run_drc.py --path={test_dir}/{device_name}_pcells.gds --variant="A" > {pattern_log}
    """
    check_call(call_str, shell=True)


@pytest.mark.parametrize("device_name", get_devices_list("fet"))
@pytest.mark.dependency(depends=["test_gds_generation", "test_cdl_generation"])
def test_lvs_run(device_name):

    file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    file_path
                )
            )
        )
    )
    
    lvs_path = "rules/klayout/lvs"
    lvs_dir = os.path.join(root_path, lvs_path)

    test_dir = os.path.join(file_path, "testcases")
    output_path = os.path.join(test_dir, f"fet_logs")
    pattern_log = f"{output_path}/{device_name}_lvs.log"
    
    # Creating output dir
    os.makedirs(output_path, exist_ok=True)

    call_str = f"""
    python3 {lvs_dir}/run_lvs.py --design={test_dir}/{device_name}_pcells.gds --net={device_name}_pcells.cdl --gf180mcu="A" > {pattern_log}
    """
    check_call(call_str, shell=True)

    f = open(pattern_log)
    log_data = f.readlines()
    f.close()
    print(log_data[-2])

    if "ERROR" in log_data[-2]:
        assert False
    else:
        assert True
