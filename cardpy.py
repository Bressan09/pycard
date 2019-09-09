# coding=utf-8
from typing import List

from smartcard.CardRequest import CardRequest
from smartcard.CardType import AnyCardType
from smartcard.util import toHexString

from Utils.Classes.RSA.RSAPublicKey import RSAPublicKey
from Utils.Convert import convert_hex_str_2_int_arr, convert_int_2_hex_str, convert_sfi_to_param2, convert_hex_str_2_int
from Utils.EMVValues.CaPublicKeys import ca_public_keys
from Utils.EMVValues.TerminalTags import get_terminal_tag_value
from Utils.Parse import parse_afl_list, parse_sfi, parse_cdol_value, parse_aip
from Utils.TlvParser import TlvParser
from Utils.Util import get_issuer_public_key, get_icc_certificate, get_n_bytes
from Utils.Wrappers.CardConnectionWrapper import GenericCardConnection

tlvParser = TlvParser()

card_type = AnyCardType()
card_request = CardRequest(timeout=None, cardType=card_type)
card_service = card_request.waitforcard()
card_connection = card_service.connection
card_connection = GenericCardConnection(card_connection)

cdol = None
signed_records = []
card_tags = {}

application = 'A0000000041010'

# Select Application
# Select Application returns the FCI (File Control Information)
# The Tag 9F38 contains the PDOL (Processing Options Data Object List)
# to use on the GPO (Get Processing Options)
card_connection.build_apdu(cla=0x00,
                           ins=0xA4,
                           p1=0x04,
                           p2=0x00,
                           data=convert_hex_str_2_int_arr(application)).send()

# GPO
# Returns the AIP Tag 0x82 (Application Interchange Profile)
# Returns the AFL Tag 0x94 (Application File Locator)
card_connection.build_apdu(cla=0x80,
                           ins=0xA8,
                           p1=0x00,
                           p2=0x00,
                           data=[0x83, 0x00]).send()

aip_value = tlvParser.parse(card_connection.response)['82:V']
aip_value = parse_aip(aip_value)

print(aip_value)

afl_value = tlvParser.parse(card_connection.response)['94:V']
afl_blocks: List[str] = parse_afl_list(afl_value)

for block in afl_blocks:
    sfi, firstRecord, lastRecord, signedRecord = parse_sfi(block)
    sfiP2 = convert_sfi_to_param2(sfi)  # Get SFI to be used on P2
    for i in range(firstRecord, lastRecord + 1):
        print('*' * 100)
        print(f'Read SFI {sfi} - Record {i} - sfiP2 = {convert_int_2_hex_str(sfiP2)}')
        print('*' * 100)
        card_connection.build_apdu(cla=0x00, ins=0xB2, p1=i, p2=sfiP2).send()
        parsed_record = tlvParser.parse(card_connection.response)
        card_tags = {**parsed_record.children, **card_tags}
        if i in range(0, signedRecord + 1):
            signed_records.append(parsed_record)

for tag in card_tags:
    print(card_tags[tag])

cdol = card_tags['8C'].value
cdol_array = parse_cdol_value(cdol)
cdol_data = ''

for cdolTag in cdol_array:
    value = ''
    if cdolTag.tag == '9F4C':
        card_connection.build_apdu(cla=0x00,
                                   ins=0x84,
                                   p1=0x00,
                                   p2=0x00).send()
        value = toHexString(card_connection.response).replace(' ', '')
    else:
        value = get_terminal_tag_value(cdolTag.tag)
    cdolTag = cdolTag._replace(value=value)
    cdol_data = cdol_data + value
    print(cdolTag)

card_connection.build_apdu(cla=0x80,
                           ins=0xAE,
                           p1=0x40,
                           p2=0x00,
                           data=convert_hex_str_2_int_arr(cdol_data)).send()

parsed = tlvParser.parse(card_connection.response)
print(parsed)

card_connection.disconnect()
print(signed_records)
print(card_tags)

print('*' * 100)
print(f'OFFLINE DATA AUTHENTICATION BEGIN')
print('*' * 100)

print('*' * 100)
print(f'USE CA PUBLIC KEY TO GET ISSUER PUBLIC KEY')
print('*' * 100)
ca_public_key_values = ca_public_keys[application[0:10]][card_tags['8F'].value]
ca_public_key_modulus = convert_hex_str_2_int(ca_public_key_values['modulus'])
ca_public_key_exponent = ca_public_key_values['exponent']
issuer_public_key = convert_hex_str_2_int(card_tags['90'].value)
ca_public_key = RSAPublicKey(ca_public_key_modulus, ca_public_key_exponent)
decrypted = ca_public_key.decrypt(issuer_public_key)
issuer_public_key_decrypted = convert_int_2_hex_str(decrypted)

assert get_n_bytes(issuer_public_key_decrypted, 1)[0] == '6A'
assert get_n_bytes(issuer_public_key_decrypted, 1, 1)[0] == '02'

pan_leftmost_digits = get_n_bytes(issuer_public_key_decrypted, 4, 2)[0].replace('FF', '')
assert card_tags['5A'].value.startswith(pan_leftmost_digits)
print(issuer_public_key_decrypted)

