from filecmp import cmp
from pathlib import Path

# import pytest

# from dls_motorhome._snippets import P_VARIABLE_API
# from dls_motorhome.group import Group

# def test_Group_class_is_context_manager():
#     assert hasattr(Group(), "__enter__")
#     assert hasattr(Group(), "__exit__")


# def test_Group_class_has_axes_attr():
#     assert hasattr(Group(), "axes")


# def test_plc_number_set_to_default_if_not_specified():
#     assert Group().plc_number == 9


# def test_plc_number_set_to_argument_parameter():
#     assert Group(plc_number=10).plc_number == 10


# def test_plc_number_must_be_within_range():
#     plc_number_min = 8
#     plc_number_max = 32
#     with pytest.raises(ValueError):
#         Group(plc_number=plc_number_max + 1)
#         Group(plc_number=plc_number_min - 1)
#         Group(plc_number=10.0)


# def test_Group_object_has_Pvar_api_in_string_list():
#     g = Group()
#     assert P_VARIABLE_API in g.code()


# def test_code_starts_with_CLOSE():
#     g = Group()
#     assert "CLOSE" in g.code().split("\n")[0]


# def test_timer_code_snippet_has_plc_number():
#     g = Group(plc_number=12)
#     lines = [line for line in g.code().split("\n") if "#define timer" in line]
#     assert "i(5111+(12&30)*50+12%2)" in lines[0]


# def test_code_has_Milliseconds_defined():
#     g = Group()
#     lines = [line for line in g.code().split("\n") if "#define MilliSeconds" in line]
#     print(lines)
#     assert "* 8388608/i10" in lines[0]


def test_plc11_ft_hm():
    from dls_motorhome.commands import (
        motor,
        group,
        plc,
        Controller,
        PostHomeMove,
        home_rlim,
    )

    tmp_file = "/tmp/plc11_ft_hm.plc"
    with plc(plc_num=11, controller=Controller.brick, filepath=tmp_file):

        motor(axis=1, jdist=0, post_home=PostHomeMove.none)
        motor(axis=2, jdist=0, post_home=PostHomeMove.none)
        motor(axis=4, jdist=0, post_home=PostHomeMove.none)
        motor(axis=5, jdist=0, post_home=PostHomeMove.none)

        with group(group_num=2, axes=[1, 2]):
            home_rlim()

        with group(group_num=3, axes=[4, 5]):
            home_rlim()

        this_path = Path(__file__).parent

    example = this_path / "examples" / "PLC11_FT_HM.pmc"
    assert cmp(tmp_file,  example), f"files {tmp_file} and {example} do not match"
