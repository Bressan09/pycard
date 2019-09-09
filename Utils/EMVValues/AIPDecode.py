# coding=utf-8
aip_meaning = ['RFU',
               'SDA supported',
               'DDA supported',
               'Cardholder verification is supported',
               'Terminal risk management is to be performed',
               'Issuer authentication is supported',
               'RFU',
               'CDA supported']


def get_aip(bit: int) -> str:
    """
    Get the bit meaning on the AIP
    :param bit: number of the bit
    :return: meaning of the bit
    """
    return aip_meaning[bit]
