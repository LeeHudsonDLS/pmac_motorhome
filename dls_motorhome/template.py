from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class Template:
    jinja_file: Optional[str]
    args: Dict[str, Any]
    function: Optional[Callable]
    custom_text: str = ""
