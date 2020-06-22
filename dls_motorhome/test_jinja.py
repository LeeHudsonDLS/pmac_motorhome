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
        print(f"jinja path is {jinja_path}")
        self.templateLoader = FileSystemLoader(searchpath=jinja_path)
        self.environment = Environment(
            loader=self.templateLoader, trim_blocks=False, lstrip_blocks=False
        )

    def render(self, template_name: str, **args) -> str:
        template = self.environment.get_template(template_name)
        output = template.render(**args)

        return output


class Group:
    def __init__(self, axes: List[int], plc: int = 9) -> None:
        self.axes = axes
        self.plc = plc

    def _all_axes(self, template: str, separator: str) -> str:
        all = [template.format(axis) for axis in self.axes]
        return separator.join(all)

    @property
    def jog_axes(self) -> str:
        return self._all_axes("#{0}J^*", " ")

    @property
    def set_large_jog_distance(self) -> str:
        return self._all_axes("m{0}72=100000000*(-i{0}23/ABS(i{0}23))", " ")

    @property
    def in_pos(self) -> str:
        return self._all_axes("m{0}40", "&")

    @property
    def following_err(self) -> str:
        return self._all_axes("m{0}42", "|")


s = SnippetGenerator()

g = Group([1, 2])
print(s.render("pre_home_move.pmc.jinja", group=g))
