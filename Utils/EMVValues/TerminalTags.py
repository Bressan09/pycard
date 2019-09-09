# coding=utf-8
terminal_tags = {
    '9F02': '000000000001',
    '9F03': '000000000000',
    '9F1A': '0076',
    '95': '0000200000',
    '5F2A': '0986',
    '9A': '010101',
    '9C': '00',
    '9F37': '01020304',
    '9F35': '12',
    '9F45': '0102',
    '9F34': '000102',
    '9F4C': '0102030405060708',
    '9F21': '204200',
    '9F7C': '0000000000000000000000000000000000000000'
    }


def get_terminal_tag_value(tag):
    try:
        return terminal_tags[tag]
    except KeyError:
        return f'Meaning Unknown for tag "{tag}"'
