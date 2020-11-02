import os
import subprocess
import sys
from importlib import import_module
from pathlib import Path
from shutil import copytree, rmtree

from click.testing import CliRunner

from converter.converter import motion

ROOT_DIR = Path(__file__).parent.parent

# TODO add a test for the 'file' entrypoint when it is working


def test_bl02i_convert():
    """
    Test conversion of an entire motion area
    """

    def junk(char: str):
        if str == " " or str == "\t":
            return False
        else:
            return True

    # use a fixed folder name in temp to assist in debugging
    test_root = Path("/tmp/BL02I_Motion")

    motion_dir = ROOT_DIR / "tests" / "converter" / "BL02I_Motion"

    if test_root.exists():
        rmtree(test_root)
    copytree(motion_dir, test_root)

    runner = CliRunner()
    result = runner.invoke(
        motion,
        str(test_root),
        catch_exceptions=False,
    )
    # dump results of the click entrypoint invocation
    print(result.output)

    # now execute the generated code
    new_code = test_root / "generate_homing_plcs2.py"
    assert new_code.exists(), "failed to generate generate_homing_plcs2.py"

    # make sure import_module can find the generate_homing_plcs2.py module
    sys.path.append(str(test_root))
    os.chdir(str(test_root))
    # execute the new module
    import_module(str(new_code.stem))

    # now check that the generated PLCs match the previous PLCs
    homing_plcs = test_root.glob("./*/*/PLC*_HM.pmc")

    mismatches = 0
    mismatch = "The following PLCs did not match the originals:\n\n"
    for new_plc in homing_plcs:
        relative = new_plc.relative_to(test_root)
        original = motion_dir / relative

        command = f"diff -b {original} {new_plc}"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()

        if process.returncode != 0:
            mismatches += 1
            mismatch += f"{original} {new_plc}\n"
    assert mismatches == 0, mismatch
