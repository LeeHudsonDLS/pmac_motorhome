import re
import sys
from importlib import import_module, reload
from pathlib import Path

import click

THIS_DIR = Path(__file__).parent


@click.argument("motorhome_file", type=click.Path(dir_okay=False))
def convert(motorhome_file):

    file = Path(motorhome_file)
    module_name = file.stem
    with file.open("r") as stream:
        filetext = stream.read()

    # make sure import_module can find the motorhome_file
    sys.path.append(str(file.parent))
    # make sure motorhome_file can import the motorhome.py shim
    sys.path.append(str(THIS_DIR))

    matches = re.findall('^[^#]*if name == "([^"]*)"', filetext, flags=re.M)

    module = None
    for i, m in enumerate(matches):
        plc_name = f"PLC{i+17}_{m}_HM.pmc"
        print(plc_name)
        sys.argv = ["exename", plc_name]
        if not module:
            module = import_module(module_name)
        else:
            reload(module)
