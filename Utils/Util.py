# coding=utf-8
from typing import Union, Tuple, Mapping

from Utils.Classes.EmvTag import EmvTag
from Utils.Classes.RSA.RSAPublicKey import RSAPublicKey
from Utils.Convert import convert_hex_str_2_int, convert_int_2_hex_str
from Utils.EMVValues.CaPublicKeys import ca_public_keys


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


def get_issuer_public_key(application: str, card_tags: Mapping[str, EmvTag]):
    ca_key = ca_public_keys[application[0:10]][card_tags['8F'].value]
    ca_key_modulus = convert_hex_str_2_int(ca_key['modulus'])
    ca_key_exponent = ca_key['exponent']
    issuer_public_key = card_tags['90'].value
    issuer_public_key_int = convert_hex_str_2_int(issuer_public_key)
    ca_ipk = RSAPublicKey(ca_key_modulus, ca_key_exponent)
    decrypted = ca_ipk.decrypt(issuer_public_key_int)
    issuer_public_key_decrypted = convert_int_2_hex_str(decrypted)
    print(issuer_public_key_decrypted)
    return issuer_public_key_decrypted[30:-42]


def get_icc_certificate(ipk_certificate: str, card_tags: Mapping[str, EmvTag]):
    ipk_certificate_modulus = convert_hex_str_2_int(ipk_certificate)
    ipk_certificate_exponent = convert_hex_str_2_int(card_tags['9F32'].value)
    icc_public_key = card_tags['9F46'].value
    icc_public_key_int = convert_hex_str_2_int(icc_public_key)
    ca_ipk = RSAPublicKey(ipk_certificate_modulus, ipk_certificate_exponent)
    decrypted = ca_ipk.decrypt(icc_public_key_int)
    icc_public_key_decrypted = convert_int_2_hex_str(decrypted)
    print(icc_public_key_decrypted)
