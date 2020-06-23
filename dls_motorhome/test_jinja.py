from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader

this_path = Path(__file__).parent
jinja_path = this_path.parent / "snippets"

templateLoader = FileSystemLoader(searchpath=jinja_path)
environment = Environment(loader=templateLoader)


class SnippetGenerator:
    def __init__(self) -> None:
        this_path = Path(__file__).parent
        jinja_path = this_path.parent / "snippets"
        self.templateLoader = FileSystemLoader(searchpath=jinja_path)
        self.environment = Environment(
            loader=self.templateLoader, trim_blocks=False, lstrip_blocks=False
        )

    def render(self, template_name: str, **args) -> str:
        template = self.environment.get_template(template_name)
        output = template.render(**args)

        return output


class Group:
    def __init__(self, axes: List[int], group_num: int = 9) -> None:
        self.axes = axes
        self.comments: str = f'; commments placeholder for group {group_num}'
        self.group_num = group_num

    def _all_axes(self, template: str, separator: str) -> str:
        all = [template.format(axis) for axis in self.axes]
        return separator.join(all)

    def jog_axes(self) -> str:
        return self._all_axes("#{0}J^*", " ")

    def set_large_jog_distance(self) -> str:
        return self._all_axes("m{0}72=100000000*(-i{0}23/ABS(i{0}23))", " ")

    def in_pos(self) -> str:
        return self._all_axes("m{0}40", "&")

    def following_err(self) -> str:
        return self._all_axes("m{0}42", "|")


class Plc:
    def __init__(self, plc_num: int) -> None:
        self.plc_num = plc_num
        self.groups: List[Group] = []

    def add_group(self, group: Group):
        self.groups.append(group)

    @property
    def count(self) -> int:
        return len(self.groups)


s = SnippetGenerator()
p = Plc(11)

g1 = Group([1, 2], 2)
g2 = Group([3, 4], 3)
p.add_group(g1)
p.add_group(g2)

print(s.render("plc.pmc.jinja", plc=p))
