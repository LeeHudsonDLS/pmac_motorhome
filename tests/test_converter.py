from pathlib import Path

from converter.motionarea import MotionArea

ROOT_DIR = Path(__file__).parent.parent

# TODO add a test for the 'file' entrypoint when it is working


def __test_bl02i_convert():
    """
    Test conversion of an entire motion area
    """
    motion_dir = ROOT_DIR / "tests" / "converter" / "BL02I_Motion"

    motionarea = MotionArea(motion_dir)

    motionarea.make_old_motion()
    motionarea.make_new_motion()
    motionarea.check_matches()


def test_bl08j_convert():
    """
    Test conversion of an entire motion area
    """
    motion_dir = ROOT_DIR / "tests" / "converter" / "BL08J_Motion"

    motionarea = MotionArea(motion_dir)

    motionarea.make_old_motion()
    motionarea.make_new_motion()
    motionarea.check_matches()
