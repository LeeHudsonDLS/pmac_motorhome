from pathlib import Path

from converter.converter import convert

ROOT_DIR = Path(__file__).parent.parent


def test_bl02i_convert():
    generator_code = ROOT_DIR / "tests" / "converter" / "BL02I_generate_homing_plcs.py"

    convert(generator_code)
