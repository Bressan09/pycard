from typing import Mapping
from typing import List

from src.Classes.Converter import Converter
from src.Classes.RSA.RSAPublicKey import RSAPublicKey
from src.Classes.TerminalClasses.TerminalAcceptableAid import TerminalAcceptableAid
from src.Classes.TerminalClasses.TerminalTag import TerminalTag
import xml.etree.ElementTree as ET


def parse_terminal_tag_file(file_path: str) -> Mapping[str, TerminalTag]:
    terminal_tags = {}
    tree = ET.parse(file_path)
    root = tree.getroot()
    for child in root:
        tag_name = child.attrib['name']
        tag_value = child.attrib['value']
        tag_meaning = child.attrib['meaning']
        terminal_tags[tag_name] = TerminalTag(tag_name, tag_value, tag_meaning)
    return terminal_tags


def parse_terminal_acceptable_aids(file_path: str) -> List[TerminalAcceptableAid]:
    acceptable_aids = []
    tree = ET.parse(file_path)
    root = tree.getroot()
    for child in root:
        aid_name = child.attrib['name']
        aid_partial = True if child.attrib['partial'] == 'true' else False
        acceptable_aids.append(TerminalAcceptableAid(aid_name, aid_partial))
    return acceptable_aids


def parse_certificate_authority_public_keys(file_path: str) -> Mapping[str, Mapping[str, RSAPublicKey]]:
    certificate_authority_public_key = {}
    tree = ET.parse(file_path)
    root = tree.getroot()
    for child in root:
        aid = child.tag
        aid_keys = {}
        for key in child:
            index = key.attrib['index']
            exponent = int(key.attrib['exponent'], 10)
            modulus = Converter().set_hex_str(key.attrib['modulus']).get_as_int()
            aid_keys[index] = RSAPublicKey(modulus, exponent)
        certificate_authority_public_key[aid] = aid_keys
    return certificate_authority_public_key
