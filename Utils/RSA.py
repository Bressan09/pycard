# coding=utf-8
from Utils.Classes.RSA.RSAPublicKey import RSAPublicKey
from Utils.Convert import convert_hex_str_2_int, convert_int_2_hex_str
from Utils.EMVValues.CaPublicKeys import ca_public_keys

ca_key = ca_public_keys['A000000004']['05']

ca_key_modulus = convert_hex_str_2_int(ca_key['modulus'])
ca_key_exponent = ca_key['exponent']
issuer_public_key = ('0160D9786A87CBCCE94E4FFB07333BB3ED704C4EF31D933A770172632717B367DD75C22D962BF600C2279D0BE2FE30DFE'
                     '06BA1637E39E2AC9C5096466D17D5D3507659FE5474174E60EFA6936B34BF789BAB07F4DE27C84E12D62EE7CFCCC6B14E'
                     'B57A8CA4B3814645712D4B067A7C8BE1A223C594619D7569B9D2DF03E1AB742C07E0050027EA72202D5B6F301217F81A0'
                     'B53AE612DDBD81CC887FE72066FAD8C1CEEE8FD6846A3A511C3DE10CA8930')

issuer_public_key_int = convert_hex_str_2_int(issuer_public_key)

ca_ipk = RSAPublicKey(ca_key_modulus, ca_key_exponent)
decrypted = ca_ipk.decrypt(issuer_public_key_int)
print(convert_int_2_hex_str(decrypted))
