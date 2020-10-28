from pathlib import Path

from click.testing import CliRunner

from converter.converter import convert

ROOT_DIR = Path(__file__).parent.parent


def test_bl02i_convert():
    generator_code = ROOT_DIR / "tests" / "converter" / "BL02I_generate_homing_plcs.py"
    tmp = Path("/tmp") / "generate_homing_plcs2.py"

    runner = CliRunner()
    result = runner.invoke(
        convert, [str(generator_code), str(tmp)], catch_exceptions=False
    )

    print(result.output)
