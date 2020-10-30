from pathlib import Path

from click.testing import CliRunner

from converter.converter import file, motion

ROOT_DIR = Path(__file__).parent.parent


def test_bl02i_convert():
    generator_code = ROOT_DIR / "tests" / "converter" / "BL02I_generate_homing_plcs.py"
    tmp = Path("/tmp") / "generate_homing_plcs2.py"

    motion_dir = ROOT_DIR / "tests" / "converter" / "BL02I_Motion"

    runner = CliRunner()
    result = runner.invoke(
        # file,
        # ["--infile", str(generator_code), "--outfile", str(tmp)],
        motion,
        str(motion_dir),
        catch_exceptions=False,
    )

    print(result.output)
