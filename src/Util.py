# coding=utf-8
from typing import Union, Tuple

from src.Convert import convert_hex_str_2_int


def get_n_bytes(hex_str: str,
                byte_qtd: Union[str, int],
                offset: Union[str, int] = 0) -> Tuple[str, str]:
    """
    Get N bytes of the provided hex_str
    """
    if isinstance(byte_qtd, str):
        byte_qtd = convert_hex_str_2_int(byte_qtd)
    if isinstance(offset, str):
        offset = convert_hex_str_2_int(offset)
    offset *= 2
    final = offset + byte_qtd * 2
    return hex_str[offset:final], hex_str[final:]


