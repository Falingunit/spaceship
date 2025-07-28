from enum import Enum
import re

class HUDAlignment(Enum):
    RIGHT = 0
    CENTER = 1
    LEFT = 2

class HUDElement():
    def __init__(self, template: str = '', values: dict[str, str] = dict(), align: HUDAlignment = HUDAlignment.CENTER) -> None:
        self._template = template
        self._values = values
        self.compiled_text = ''
        self.alignment = align

        self.resolve_template()

    @property
    def template(self) -> str:
        return self.template
    @template.setter
    def template(self, value: str):
        self._template = value
        self.resolve_template()
    
    @property
    def values(self) -> dict[str, str]:
        return self._values
    @values.setter
    def values(self, value: dict[str, str]):
        self._values = value
        self.resolve_template()

    def resolve_template(self):
        
        params = self.values.keys()
        regex_pattern = re.compile('`|`'.join(re.escape(param) for param in params))

        self.compiled_text = regex_pattern.sub(lambda match: self.values[match.group(0)], self.template)

class HUD():
    def __init__(self, top_huds: list[HUDElement], bottom_huds: list[HUDElement]):
        self._top_huds = top_huds
        self._bottom_huds = bottom_huds