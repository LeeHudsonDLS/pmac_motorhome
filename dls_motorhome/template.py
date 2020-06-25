from dataclasses import dataclass
from typing import Dict


@dataclass
class Template:
    jinja_file: str
    args: Dict[str, str]
    custom_text: str = ""
