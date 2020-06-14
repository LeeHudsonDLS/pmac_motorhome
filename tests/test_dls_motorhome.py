from dls_motorhome import Group


def test_Group_class_is_context_manager():
    assert hasattr(Group(), "__enter__")
    assert hasattr(Group(), "__exit__")
