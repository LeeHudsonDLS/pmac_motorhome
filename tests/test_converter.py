import re
import sys
from importlib import import_module, reload
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent


def test_bl02i_convert():
    modules = ROOT_DIR / "converter"
    sys.path.append(modules)
    tests = ROOT_DIR / "tests" / "converter"
    sys.path.append(str(tests))

    filename = "BL02I_generate_homing_plcs"
    filepath = tests / f"{filename}.py"
    with filepath.open("r") as stream:
        filetext = stream.read()

    matches = re.findall('^[^#]*if name == "([^"]*)"', filetext, flags=re.M)

    module = None
    for m in matches:
        print(f"{m}")
        sys.argv = ["exename", f"PLC17_{m}_HM.pmc"]
        if not module:
            module = import_module(filename)
        else:
            reload(module)

