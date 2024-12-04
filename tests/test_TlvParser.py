from unittest import TestCase

from src.Classes.EmvTag import EmvTag
from src.Classes.TlvParser import TlvParser


class TestTlvParser(TestCase):
    def test_tlv_parser_simple_tag(self):
        parser = TlvParser()
        tag_map = parser.parse('94081801020120020400')
        tag_94 = EmvTag('94', '1801020120020400', '94:1')
        self.assertEqual(tag_map, tag_94)

    def test_tlv_parser_multi_tag(self):
        parser = TlvParser()
        tag_map = parser.parse('770E8202390094081801020120020400')
        tag_94 = EmvTag('94', '1801020120020400', '94:1')
        tag_82 = EmvTag('82', '3900', '82:1')
        tag_77 = EmvTag('77', '8202390094081801020120020400', '77:1', {'82': tag_82, '94': tag_94})
        self.assertEqual(tag_map, tag_77)

    def test_tlv_parser_multi_tag_complex(self):
        parser = TlvParser()
        tag_map = parser.parse(('6F1A8407A0000000041010A50F'
                                '500A4D617374657243617264870101'))
        tag_50 = EmvTag('50', '4D617374657243617264', '55:1')
        tag_87 = EmvTag('87', '01', '87:1')
        tag_A5 = EmvTag('A5', '500A4D617374657243617264870101', 'A5:1', {'50': tag_50, '87': tag_87})
        tag_84 = EmvTag('84', 'A0000000041010', '84:1')
        tag_6F = EmvTag('6F', '8407A0000000041010A50F500A4D617374657243617264870101', '6F:1',
                        {'84': tag_84, 'A5': tag_A5})
        self.assertEqual(tag_map, tag_6F)

    def test_tlv_parser_multi_tag_duplicated_tag(self):
        parser = TlvParser()
        tag_map = parser.parse(('6F6D840E325041592E5359532E4444463031A55BBF0C5861294F07A0000000031010500C56495341204352454449544F8701019F120C56495341204352454449544F612B4F07A0000000032010500D5649534120454C454354524F4E8701029F120D5649534120454C454354524F4E'))
        self.assertEqual(tag_map, {})
