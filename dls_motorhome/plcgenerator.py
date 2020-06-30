from pathlib import Path

from jinja2 import Environment, FileSystemLoader

this_path = Path(__file__).parent
jinja_path = this_path.parent / "snippets"

templateLoader = FileSystemLoader(searchpath=jinja_path)
environment = Environment(loader=templateLoader)


class PlcGenerator:
    def __init__(self) -> None:
        this_path = Path(__file__).parent
        jinja_path = this_path / "snippets"
        self.templateLoader = FileSystemLoader(searchpath=jinja_path)
        self.environment = Environment(
            loader=self.templateLoader,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def render(self, template_name: str, **args) -> str:
        template = self.environment.get_template(template_name)
        output = template.render(**args)

        return output
