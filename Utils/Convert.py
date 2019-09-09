# coding=utf-8
from typing import List


def convert_hex_str_2_int_arr(hex_str: str) -> List[int]:
    """
    Convert Hex String to Int Array, e.g. "ABCD" to [0xAB, 0xCD]
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


def convert_int_2_hex_str(number: int) -> str:
    """
    Convert integer to hex string representation, e.g. 12 to '0C'
    """
    if number < 0:
        raise ValueError('Invalid number to hexify - must be positive')

    result = hex(int(number)).replace('0x', '').upper()
    if len(result) % 2 == 1:
        result = '0{}'.format(result)
    return result


def convert_hex_str_2_int(hex_str: str) -> int:
    """
    Convert Hex String to Integer, e.g. '0C' to 12
    """
    return int(hex_str, 16)


def convert_int_2_bin_str(number: int) -> str:
    """
    Convert Int to Binary String, e.g. 12 to '00001100'
    """
    return format_bin_str(bin(number))


def convert_hex_str_2_bin_str(hex_str: str) -> str:
    """
    Convert Hex String to Binary String, e.g. '0C' to '00001100'
    """
    bin_str = ''
    for i in range(0, len(hex_str), 2):
        bin_str += format_bin_str(bin(int(hex_str[i:i + 2], 16)))
    return bin_str


def format_bin_str(bin_str: str) -> str:
    """
    Format Binary String, e.g. '00110' to '00000110'
    """
    return bin_str.replace('0b', '').rjust(8, '0')


def convert_sfi_to_param2(sfi: int) -> int:
    """
    Convert sfi number to sfi to be used on READ RECORD APDU
    :param sfi: sfi integer
    :return: sfi integer to be used as P2 on APDU
    """
    return (sfi << 3) + 4
