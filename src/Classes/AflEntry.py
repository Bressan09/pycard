from __future__ import annotations

from dataclasses import dataclass, field, InitVar
from typing import List

from src.Classes.Converter import Converter
from src.Util import get_n_bytes


@dataclass
class AflEntry:
    """
    Stores the Afl Entry
    """
    sfi_read: str = field(init=False)
    sfi_number: int = field(init=False)
    sfi_p2: int = field(init=False)
    start_record: int = field(init=False)
    end_record: int = field(init=False)
    signed_record: int = field(init=False)
    afl_entry: InitVar[str]

    def __post_init__(self, afl_entry: str):
        self.sfi_read = get_n_bytes(afl_entry, 1)[0]
        self.start_record = Converter().set_hex_str(get_n_bytes(afl_entry, 1, 1)[0]).get_as_int()
        self.end_record = Converter().set_hex_str(get_n_bytes(afl_entry, 1, 2)[0]).get_as_int()
        self.signed_record = Converter().set_hex_str(get_n_bytes(afl_entry, 1, 3)[0]).get_as_int()
        read_number = Converter().set_hex_str(self.sfi_read).get_as_int()
        self.sfi_number = read_number >> 3
        self.sfi_p2 = read_number + 4

    @classmethod
    def build_entries_from_response(cls, afl: str) -> List[AflEntry]:
        afl_list = []
        for afl_entry in [afl[i:i + 8] for i in range(0, len(afl), 8)]:
            afl_list.append(AflEntry(afl_entry))
        return afl_list
