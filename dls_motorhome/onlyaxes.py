from typing import List, Optional

from .group import Group


class OnlyAxes:
    # this class variable holds the current axis filter for a group
    the_only_axes: Optional["OnlyAxes"] = None

    def __init__(self, group: Group, axes: List[int]) -> None:
        self.axes = axes
        self.group = group

    def __enter__(self):
        assert (
            not OnlyAxes.the_only_axes
        ), "cannot use only_axes within another only_axes"

        OnlyAxes.the_only_axes = self
        self.group.add_action(Group.set_axis_filter, axes=self.axes)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        OnlyAxes.the_only_axes = None
        # empty axis filter means reset the axis filter
        self.group.add_action(Group.set_axis_filter, axes=[])
