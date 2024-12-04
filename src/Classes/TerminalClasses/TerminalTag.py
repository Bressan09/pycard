from dataclasses import dataclass


@dataclass
class TerminalTag:
    tag_name: str
    value: str
    meaning: str
