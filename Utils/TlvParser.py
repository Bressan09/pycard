# coding=utf-8
from typing import List, Union, Dict

from smartcard.util import toHexString

from Utils.Parse import parse_tlv_tag, parse_tlv_length
from Utils.Util import get_n_bytes
from .Classes.EmvTag import EmvTag


class TlvParser:

    # noinspection PySameParameterValue
    def parse(self, tlv: Union[str, List[int]], is_propagated: bool = False) -> Union[Dict[str, EmvTag], EmvTag]:
        if isinstance(tlv, list):
            tlv = toHexString(tlv)

        tlv = tlv.replace(' ', '')
        tag, remaining, is_constructed = parse_tlv_tag(tlv)
        length, remaining = parse_tlv_length(remaining)
        value, remaining = get_n_bytes(remaining, length)

        emv_tag = EmvTag(tag, value, None)
        tag_map = {tag: emv_tag}
        if is_constructed:
            if remaining:
                raise Exception(
                    f'Not constructed Tag {tag} parsed but '
                    f'still has {int(len(remaining) / 2)} byte(s) remaining: '
                    f'{remaining}')
            emv_tag.add_child(self.parse(value, True))

        if remaining:
            tag_map = {**self.parse(remaining, True)}

        tag_map[tag] = emv_tag
        if is_propagated:
            return tag_map
        else:
            return tag_map[tag]


if __name__ == '__main__':
    parser = TlvParser()
    tag_map2 = parser.parse('770E8202390094081801020120020400')
    print(tag_map2['94'])
    print(parser.parse(('6F1A8407A0000000041010A50F'
                        '500A4D617374657243617264870101')))
