from typing import Mapping, Optional
from dataclasses import dataclass

from src.Classes.EmvTag import EmvTag


@dataclass
class CardTagMap:
    tags: Mapping[str, EmvTag]

    def __getitem__(self, key: str) -> Optional[EmvTag]:
        if len(key.split(':')) == 1:
            key = key + ':1'

        return self.tags[key] if key in self.tags else None
