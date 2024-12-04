from typing import List, Union, Dict, Tuple, Mapping

from smartcard.util import toHexString

from src.Classes.MetaClass.SingletonMeta import SingletonMeta

from src.Convert import convert_hex_str_2_bin_str
from src.Util import get_n_bytes
from src.Classes.EmvTag import EmvTag


class TlvParser(metaclass=SingletonMeta):

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def _build_tag_name(tag: str, seq: int):
        return f'{tag}:{seq}'

    def parse_child(self, child_tlv: str) -> Mapping[str, EmvTag]:
        tag, remaining, is_constructed = self.parse_tlv_tag(child_tlv)
        tag_counter = {tag: 1}
        length, remaining = self.parse_tlv_length(remaining)
        value, remaining = get_n_bytes(remaining, length)
        emv_tag = EmvTag(tag, value, self._build_tag_name(tag, tag_counter[tag]), None)
        tag_map = {self._build_tag_name(tag, 1): emv_tag}
        if is_constructed:
            emv_tag.add_child(self.parse_child(value))

        if remaining:
            remaining_tags = self.parse_child(remaining)
            for _tag in remaining_tags:
                real_tag = _tag.split(':')[0]
                if real_tag not in tag_counter:
                    tag_counter[tag] = 1
                else:
                    tag_counter[tag] = tag_counter[tag] + 1
                tag_map[self._build_tag_name(real_tag, tag_counter[tag])] = remaining_tags[_tag]
        return tag_map

    def parse(self,
              tlv: Union[str, List[int]]) -> EmvTag:

        if isinstance(tlv, list):
            tlv = toHexString(tlv)
        assert isinstance(tlv, str)
        tlv = tlv.replace(' ', '')
        tag, remaining, is_constructed = self.parse_tlv_tag(tlv)
        length, remaining = self.parse_tlv_length(remaining)
        value, remaining = get_n_bytes(remaining, length)

        emv_tag = EmvTag(tag, value, self._build_tag_name(tag, 1), None)
        if is_constructed:
            emv_tag.add_child(self.parse_child(value))

        return emv_tag
