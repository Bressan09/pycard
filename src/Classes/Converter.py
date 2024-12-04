from __future__ import annotations

from typing import Optional, List

from src.Classes.MetaClass.SingletonMeta import SingletonMeta
from src.Convert import convert_hex_str_2_int_arr, convert_int_2_hex_str, convert_hex_str_2_int, convert_int_2_bin_str, \
    convert_hex_str_2_bin_str, convert_int_arr_2_hex_str


class Converter(metaclass=SingletonMeta):
    _from_hex: Optional[str] = None
    _from_int: Optional[int] = None
    _from_int_arr: Optional[List[int]] = None

    def set_hex_str(self, from_str: str) -> Converter:
        self._from_hex = from_str
        self._from_int = None
        self._from_int_arr = None
        return self

    def set_int(self, from_int: int) -> Converter:
        self._from_hex = None
        self._from_int = from_int
        self._from_int_arr = None
        return self

    def set_int_arr(self, from_int_arr) -> Converter:
        self._from_hex = None
        self._from_int = None
        self._from_int_arr = from_int_arr
        return self

    def get_as_int_arr(self) -> List[int]:
        assert self._from_hex is not None
        return convert_hex_str_2_int_arr(self._from_hex)

    def get_as_hex_str(self) -> str:
        assert self._from_int_arr is not None or self._from_int is not None
        if self._from_int is not None:
            return convert_int_2_hex_str(self._from_int)
        else:
            return convert_int_arr_2_hex_str(self._from_int_arr)

    def get_as_int(self) -> int:
        assert self._from_hex is not None
        return convert_hex_str_2_int(self._from_hex)

    def get_as_bin_str(self) -> str:
        assert self._from_hex is not None or self._from_int is not None
        if self._from_hex is not None:
            return convert_hex_str_2_bin_str(self._from_hex)
        else:
            return convert_int_2_bin_str(self._from_int)
