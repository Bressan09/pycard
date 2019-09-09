# coding=utf-8
from typing import List, Tuple, NamedTuple

from Utils.Convert import convert_hex_str_2_int, convert_hex_str_2_bin_str
from Utils.EMVValues.AIPDecode import get_aip
from Utils.EMVValues.TagMeaning import get_tag_meaning
from Utils.Util import get_n_bytes


def parse_afl_list(afl_value: str) -> List[str]:
    """
    Get tag 94 and return it in blocks of 4 bytes
    :param afl_value: str
    :return: List[str]
    """
    return [afl_value[i:i + 8] for i in range(0, len(afl_value), 8)]


def parse_sfi(sfi_block: str) -> Tuple[int, int, int, int]:
    """
    Get an afl block with 4 bytes and separate its values in a tuple
    :param sfi_block: str of 4 bytes
    :return: Tuple[sfi_number, first_record, last_record, signed_records]
    """
    sfi = get_n_bytes(sfi_block, 1)[0]
    sfi = convert_hex_str_2_int(sfi) >> 3
    first_record = convert_hex_str_2_int(get_n_bytes(sfi_block, 1, 1)[0])
    last_record = convert_hex_str_2_int(get_n_bytes(sfi_block, 1, 2)[0])
    signed_record = convert_hex_str_2_int(get_n_bytes(sfi_block, 1, 3)[0])
    return sfi, first_record, last_record, signed_record


def parse_tlv_length(tlv: str) -> Tuple[str, str]:
    """
    Parse and HexString and returns its length
    :param tlv: str
    :return: Tuple[length, remaining_data]
    """
    length, remaining = get_n_bytes(tlv, 1)
    binary_length = convert_hex_str_2_bin_str(length)
    if binary_length.startswith('1'):
        byte_quantity = int(binary_length[1:], 2)
        length = tlv[2: 2 + byte_quantity * 2]
        remaining = tlv[2 + byte_quantity * 2:]
    return length, remaining


def parse_tlv_tag(tlv: str) -> Tuple[str, str, bool]:
    """
    Parse and HexString and returns its tag_name
    :param tlv: str
    :return: Tuple[tag_name, remaining_data, is_constructed]
    """
    tag, remaining = get_n_bytes(tlv, 1)
    binary_tag = convert_hex_str_2_bin_str(tag)
    if binary_tag.endswith('11111'):
        # There is a 2nd byte with tag value
        tag, remaining = get_n_bytes(tlv, 2)
    is_constructed = binary_tag[2:3] == '1'
    return tag, remaining, is_constructed


class CdolInfo(NamedTuple):
    """
    Stores the tag, length, value and meaning of the CDOL tag
    """
    tag: str
    length: str
    meaning: str
    value: str = ''


def parse_cdol_value(cdol: str) -> List[CdolInfo]:
    """
    Parse the value of tag 8C or 8D (CDOL1 or CDOL2) and return its Info
    :param cdol: str
    :return: List[CdolInfo[tag, length, meaning, value]]
    """
    cdol_array = []
    while cdol != '':
        tag, cdol, _ = parse_tlv_tag(cdol)
        length, cdol = parse_tlv_length(cdol)
        cdol_array.append(CdolInfo(tag=tag, length=length,
                                   meaning=get_tag_meaning(tag)))
    return cdol_array


def parse_aip(aip: str):
    """
    Receive AIP value and return functions supported by the card
    :param aip:
    :return:
    """
    bin_aip = convert_hex_str_2_bin_str(aip)
    aip_list = []
    for i in range(0, 8):
        if bin_aip[i:i + 1] == '1':
            aip_list.append(get_aip(i))
    return aip_list
