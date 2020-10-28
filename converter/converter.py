import re
import sys
from importlib import import_module, reload
from pathlib import Path
from typing import Sequence

import click

from .plc import PLC

THIS_DIR = Path(__file__).parent


@click.command()
@click.argument(
    "infile", type=click.Path(dir_okay=False), default="generate_homing_plcs.py"
)
@click.argument(
    "outfile", type=click.Path(dir_okay=False), default="generate_homing_plcs2.py"
)
def convert(infile: str, outfile: str):
    inpath = Path(infile)
    outpath = Path(outfile)
    module_name = inpath.stem
    with inpath.open("r") as stream:
        filetext = stream.read()

    # make sure import_module can find the motorhome_file
    sys.path.append(str(inpath.parent))
    # make sure motorhome_file can import the motorhome.py shim
    sys.path.append(str(THIS_DIR))

    matches = re.findall('^[^#]*if name == "([^"]*)"', filetext, flags=re.M)

    module = None
    for i, m in enumerate(matches):
        plc_name = f"PLC{i+10}_{m}_HM.pmc"
        sys.argv = ["exename", plc_name]
        if not module:
            module = import_module(module_name)
        else:
            reload(module)

    plcs = list(PLC.get_instances())
    make_code(plcs, outpath)


import_1 = "from dls_motorhome.commands import group, motor, plc\n"
import_2 = """from dls_motorhome.sequences import (
    {names}
)
"""

plc_block = """
with plc(
    plc_num={plc.plc},
    controller={plc.bricktype},
    filepath="{plc_path}",
):
"""


def make_code(plcs: Sequence[PLC], outpath: Path):
    plc_folder = outpath.parent / "PLCs"

    with outpath.open("w") as stream:
        stream.write(import_1)

        # collect all the homing sequences used for the import statement
        imports = set()
        for plc in plcs:
            for group in plc.groups.values():
                imports.add(group.sequence.name)

        imps = "\n    ".join(imports)
        stream.write(import_2.format(names=imps))

        for plc in plcs:
            plc_path = plc_folder / plc.filename
            fs = plc_block.format(plc=plc, plc_path=plc_path)
            stream.write(fs)
