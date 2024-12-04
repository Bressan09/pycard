from __future__ import annotations

from dataclasses import dataclass, field, InitVar
from typing import Optional

from src.Classes.EmvTag import EmvTag
from src.Util import get_n_bytes


@dataclass
class GpoInfo:
    """
    Stores the response of the application to the get processing options command
    """
    afl: str = field(init=False)
    aip: str = field(init=False)
    template_format: str = field(init=False)
    all_tags: Optional[EmvTag] = field(init=False)
    gpo: InitVar[EmvTag]

    def __post_init__(self, gpo: EmvTag):
        if gpo['80']:
            # Response Message Template Format 1
            parsed_gpo = gpo['80'].value
            (aip, afl) = get_n_bytes(parsed_gpo, 2)
            self.template_format = '80'
            self.aip = aip
            self.afl = afl
            self.all_tags = None
        elif gpo['77']:
            # Response Message Template Format 2
            parsed_gpo = gpo['77']
            self.template_format = '77'
            self.aip = parsed_gpo['82'].value
            self.afl = parsed_gpo['94'].value
            self.all_tags = parsed_gpo
        else:
            raise ValueError(f'Template Format {gpo.name} does not match any known format')

