import pytest

from dls_motorhome import Group
from dls_motorhome._snippets import P_VARIABLE_API


def test_Group_class_is_context_manager():
    assert hasattr(Group(), "__enter__")
    assert hasattr(Group(), "__exit__")


def test_Group_class_has_axes_attr():
    assert hasattr(Group(), "axes")


def test_plc_number_set_to_default_if_not_specified():
    assert Group().plc_number == 9


def test_plc_number_set_to_argument_parameter():
    assert Group(plc_number=10).plc_number == 10


def test_plc_number_must_be_within_range():
    plc_number_min = 8
    plc_number_max = 32
    with pytest.raises(ValueError):
        Group(plc_number=plc_number_max + 1)
        Group(plc_number=plc_number_min - 1)
        Group(plc_number=10.0)


def test_Group_object_has_Pvar_api_in_string_list():
    g = Group()
    assert P_VARIABLE_API in g.code()


def test_code_starts_with_CLOSE():
    g = Group()
    assert "CLOSE" in g.code().split("\n")[0]


def test_timer_code_snippet_has_plc_number():
    g = Group(plc_number=12)
    assert "i(5111+(12&30)*50+12%2)" in g.code()
