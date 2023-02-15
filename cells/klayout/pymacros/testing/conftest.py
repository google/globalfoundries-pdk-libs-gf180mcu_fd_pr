import os 
import glob

def pytest_addoption(parser):
    parser.addoption(
        '--device', action='store', default='fet', help='device under test name'
    )

# def pytest_generate_tests(metafunc):
#     if "device_name" in metafunc.fixturenames:
#         dev = metafunc.config.getoption("device")
#         print(dev)
#         devices = []

#         if dev : 
#             file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#             list_patt_files = glob.glob(
#                 os.path.join(file_path, "patterns", dev, "*.csv")
#             )

#             for file_path in list_patt_files:
#                 devices.append(file_path.split("/")[-1].split("_patt")[0])
    
#         metafunc.parametrize("device_name",devices) 
