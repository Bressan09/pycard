from unittest import TestCase

from src.Convert import convert_hex_str_2_int_arr, convert_int_2_hex_str


class Test(TestCase):
    def test_convert_hex_str_2_int_arr_uppercase(self):
        self.assertEqual(convert_hex_str_2_int_arr('ABCD'), [0xAB, 0xCD])

    def test_convert_hex_str_2_int_arr_lowercase(self):
        self.assertEqual(convert_hex_str_2_int_arr('abcd'), [0xAB, 0xCD])

    def test_convert_hex_str_2_int_arr_both_cases(self):
        self.assertEqual(convert_hex_str_2_int_arr('aBCd'), [0xAB, 0xCD])

    def test_convert_int_2_hex_str_1_byte(self):
        self.assertEqual(convert_int_2_hex_str(12), '0C')

    def test_convert_int_2_hex_str_more_bytes(self):
        self.assertEqual(convert_int_2_hex_str(513), '0201')