from __future__ import annotations

from typing import List

from src.Classes.Converter import Converter
from src.Classes.MetaClass.SingletonMeta import SingletonMeta


class TlvBuilder(metaclass=SingletonMeta):
    _current_value: str = ""

    def append_hex_str_value(self, value: str) -> TlvBuilder:
        self._current_value += value
        return self

    def append_int_array(self, value: List[int]) -> TlvBuilder:
        self._current_value += Converter().set_int_arr(value).get_as_hex_str()
        return self

    @staticmethod
    def get_value_ber_len(value: str) -> str:
        tag_len = len(value)//2
        final_tag_len = ''
        actual_tag_len = Converter().set_int(tag_len).get_as_hex_str()
        if tag_len > 127:
            if tag_len > 255:
                actual_tag_len = '82'
            else:
                actual_tag_len = '81'
        final_tag_len += actual_tag_len

        return final_tag_len

    def get_tlv(self, tag_name: str) -> str:
        final_tlv = tag_name
        final_tlv += self.get_value_ber_len(self._current_value)
        final_tlv += self._current_value
        return final_tlv
