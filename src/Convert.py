# coding=utf-8
from typing import List


def convert_hex_str_2_int_arr(hex_str: str) -> List[int]:
    """
    Convert Hex String to Int Array, e.g. "ABCD" to [171, 205]
    >>> convert_hex_str_2_int_arr('ABCD')
    [171, 205]
    >>> convert_hex_str_2_int_arr('AbCd')
    [171, 205]
    >>> convert_hex_str_2_int_arr('abcd')
    [171, 205]
    """
    if isinstance(hex_str, str):
        hex_str = hex_str.replace(' ', '')
        if len(hex_str) % 2 == 0:
            int_array = []
            for i in range(0, len(hex_str), 2):
                int_array.append(int(hex_str[i:i + 2], 16))
            return int_array
        else:
            raise ValueError('Param has an odd length without spaces')


def convert_int_arr_2_hex_str(int_arr: List[int]) -> str:
    """
    Convert Int Array to Hex String, e.g. [171, 205] to "ABCD"
    >>> convert_int_arr_2_hex_str([171, 205])
    'ABCD'
    """
    final_str = ""
    for i in int_arr:
        final_str += convert_int_2_hex_str(i)
    return final_str


def convert_int_2_hex_str(number: int) -> str:
    """
    Convert integer to hex string representation, e.g. 12 to '0C'
    >>> convert_int_2_hex_str(12)
    '0C'
    >>> convert_int_2_hex_str(291)
    '0123'
    """

    result = hex(int(number)).replace('0x', '').upper()
    if len(result) % 2 == 1:
        result = '0{}'.format(result)
    return result


def convert_hex_str_2_int(hex_str: str) -> int:
    """
    Convert Hex String to Integer, e.g. '0C' to 12
    >>> convert_hex_str_2_int('0C')
    12
    >>> convert_hex_str_2_int('0123')
    291
    >>> convert_hex_str_2_int('123')
    291
    """
    return int(hex_str, 16)


def convert_int_2_bin_str(number: int) -> str:
    """
    Convert Int to Binary String, e.g. 12 to '00001100'
    >>> convert_int_2_bin_str(12)
    '00001100'
    >>> convert_int_2_bin_str(0xFF)
    '11111111'
    >>> convert_int_2_bin_str(0x3FF)
    '001111111111'
    >>> convert_int_2_bin_str(0x1FFF)
    '0001111111111111'
    """
    return format_bin_str(bin(number))


def convert_hex_str_2_bin_str(hex_str: str) -> str:
    """
    Convert Hex String to Binary String, e.g. '0C' to '00001100'
    >>> convert_hex_str_2_bin_str('0C')
    '00001100'
    >>> convert_hex_str_2_bin_str('FF')
    '11111111'
    >>> convert_hex_str_2_bin_str('03FF')
    '001111111111'
    >>> convert_hex_str_2_bin_str('1FFF')
    '0001111111111111'
    """
    bin_str = ''
    for i in range(0, len(hex_str), 2):
        bin_str += format_bin_str(bin(int(hex_str[i:i + 2], 16)), 0)
    return format_bin_str(bin_str, 8)


def format_bin_str(bin_str: str, min_chars=8) -> str:
    """
    Format Binary String, e.g. '00110' to '00000110'
    >>> format_bin_str('0110', 8)
    '00000110'
    >>> format_bin_str('0110', 0)
    '0110'
    >>> format_bin_str('110', 0)
    '0110'
    >>> format_bin_str('110', 6)
    '00000110'
    """
    bin_str = bin_str.replace('0b', '')

    bin_str_len = len(bin_str)
    if bin_str_len < min_chars:
        bin_str_len = min_chars
    after_four = bin_str_len % 4
    if after_four == 0:
        bin_str_final_len = bin_str_len
    else:
        bin_str_final_len = bin_str_len + 4 - after_four

    return bin_str.rjust(bin_str_final_len, '0')


def convert_sfi_to_param2(sfi: int) -> int:
    """
    Convert sfi number to sfi to be used on READ RECORD APDU
    >>> convert_sfi_to_param2(1)
    12
    >>> convert_sfi_to_param2(2)
    20
    """
    return (sfi << 3) + 4
