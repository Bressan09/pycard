from dataclasses import dataclass


@dataclass
class DolInfo:
    """
    Stores the tag, length, value and meaning of a DOL tag
    """
    tag: str
    length: str
    meaning: str
    value: str = ''
