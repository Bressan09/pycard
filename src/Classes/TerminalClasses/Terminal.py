from __future__ import annotations

from typing import Mapping, List, Union, Optional, Callable

from smartcard.CardRequest import CardRequest
from smartcard.CardType import AnyCardType
from smartcard.PassThruCardService import PassThruCardService

from src.Classes.AflEntry import AflEntry
from src.Classes.CardTagMap import CardTagMap
from src.Classes.Converter import Converter
from src.Classes.DolInfo import DolInfo
from src.Classes.GpoInfo import GpoInfo
from src.Classes.Certificates.ICCCertificate import ICCCertificate
from src.Classes.Certificates.IssuerCertificate import IssuerCertificate
from src.Classes.MetaClass.SingletonMeta import SingletonMeta
from src.Classes.RSA.RSAPublicKey import RSAPublicKey
from src.Classes.TerminalClasses.CandidateAidEntry import CandidateAidEntry
from src.Classes.TerminalClasses.TerminalAcceptableAid import TerminalAcceptableAid
from src.Classes.TerminalClasses.TerminalTag import TerminalTag
from src.Classes.TlvParser import TlvParser
from src.ConfigParser import parse_terminal_tag_file, parse_terminal_acceptable_aids, \
    parse_certificate_authority_public_keys
from src.Wrappers.EmvCardConnectionWrapper import EmvGenericCardConnection


def request_card_connection(callback: Callable) -> Callable:
    def wrapper(self: Terminal, *args):
        assert self.card_connection is not None
        return callback(self, *args)
    return wrapper


def request_tag_map(callback: Callable) -> Callable:
    def wrapper(self: Terminal, *args):
        assert self.card_tag_map is not None
        return callback(self, *args)
    return wrapper


class Terminal(metaclass=SingletonMeta):
    tlv_parser: TlvParser = TlvParser()

    def __init__(self,
                 terminal_tags: Optional[Union[str, Mapping[str, TerminalTag]]] = None,
                 acceptable_aids: Optional[Union[str, List[TerminalAcceptableAid]]] = None,
                 ca_public_keys: Optional[Union[str, Mapping[str, Mapping[str, RSAPublicKey]]]] = None):
        if terminal_tags is not None:
            self.terminal_tags = terminal_tags
        if acceptable_aids is not None:
            self.acceptable_aids = acceptable_aids
        if ca_public_keys is not None:
            self.ca_public_keys = ca_public_keys
        self.card_connection: Optional[EmvGenericCardConnection] = None
        self.card_service: Optional[PassThruCardService] = None
        self.candidate_list: List[CandidateAidEntry] = []
        self.chosen_application: Optional[CandidateAidEntry] = None
        self.pdol_array: Optional[List[DolInfo]] = None
        self.current_gpo_info: Optional[GpoInfo] = None
        self.card_tag_map: Optional[CardTagMap] = None
        self.signed_data: str = ''

    @request_card_connection
    def choose_application(self, candidate_index: int):
        self.chosen_application = self.candidate_list[candidate_index]
        app_aid = Converter().set_hex_str(self.chosen_application.aid).get_as_int_arr()
        self.card_connection.select_application_by_name(app_aid)

    def build_pdol_value(self, pdol_request: str) -> str:
        self.pdol_array = []
        dol_value = ''
        while pdol_request != '':
            tag, pdol_request, _ = TlvParser().parse_tlv_tag(pdol_request)
            length, pdol_request = TlvParser().parse_tlv_length(pdol_request)
            terminal_tag = self.terminal_tags[tag]
            self.pdol_array.append(DolInfo(tag=tag,
                                           length=length,
                                           meaning=terminal_tag.meaning,
                                           value=terminal_tag.value))
            dol_value += terminal_tag.value
        return dol_value

    @request_card_connection
    def get_processing_options(self) -> None:
        pdol = self.card_connection.get_tlv_response()['6F']['A5']['9F38']
        if pdol:
            self.card_connection.get_processing_options(self.build_pdol_value(pdol.value))
        else:
            self.card_connection.get_processing_options('')
        card_response = self.card_connection.get_tlv_response()
        self.current_gpo_info = GpoInfo(card_response)

    @request_card_connection
    def get_application_info(self):
        assert self.current_gpo_info is not None
        afl_entries = AflEntry.build_entries_from_response(self.current_gpo_info.afl)
        card_tag_map = {}
        for afl_entry in afl_entries:
            signed = 0
            for record_number in range(afl_entry.start_record, afl_entry.end_record + 1, 1):
                self.card_connection.read_record(afl_entry.sfi_number, record_number)
                if self.card_connection.last_command_was_ok():
                    record = self.card_connection.get_tlv_response()
                    card_tag_map = {**card_tag_map, **record.children}
                    if signed < afl_entry.signed_record:
                        signed += 1
                        self.signed_data += record.value

        self.card_tag_map = CardTagMap(tags=card_tag_map)

    @request_card_connection
    def run_static_data_authentication(self):
        pass

    @request_card_connection
    @request_tag_map
    def run_dynamic_data_authentication(self):
        issuer_certificate = self._get_and_validate_issuer_certificate()
        print(issuer_certificate)

        icc_certificate = self._get_and_validate_icc_certificate(issuer_certificate)
        print(icc_certificate)
        self._send_internal_authenticate()

    @request_card_connection
    @request_tag_map
    def _get_and_validate_icc_certificate(self, issuer_certificate: IssuerCertificate) -> ICCCertificate:
        pan = self.card_tag_map['5A'].value
        # ---------------------------------------------------
        issuer_key = issuer_certificate.get_as_public_key()
        signed_icc_certificate = Converter().set_hex_str(self.card_tag_map['9F46'].value).get_as_int()
        unsigned_icc_certificate = Converter().set_int(issuer_key.decrypt(signed_icc_certificate)).get_as_hex_str()
        icc_remainder = self.card_tag_map['9F48'].value if self.card_tag_map['9F48'] else None
        icc_exponent = self.card_tag_map['9F47'].value
        icc_certificate = ICCCertificate(unsigned_icc_certificate, icc_exponent, icc_remainder)

        sda_tag_list = self.card_tag_map['9F4A'].value if self.card_tag_map['9F4A'] else None
        if sda_tag_list:
            self.signed_data += self.current_gpo_info.aip
        icc_certificate.validate(pan, self.signed_data)
        return icc_certificate

    def _send_internal_authenticate(self):
        print(self.card_tag_map['9F49'])
        self.card_connection.internal_authenticate('01020304')

    def _get_and_validate_issuer_certificate(self) -> IssuerCertificate:
        ca_pk_index = self.card_tag_map['8F'].value
        rid = self.chosen_application.aid[:10]
        ca_key = self.ca_public_keys[rid][ca_pk_index]
        # ---------------------------------------------------
        pan = self.card_tag_map['5A'].value
        # ---------------------------------------------------
        signed_issuer_certificate = Converter().set_hex_str(self.card_tag_map['90'].value).get_as_int()
        unsigned_issuer_certificate = Converter().set_int(ca_key.decrypt(signed_issuer_certificate)).get_as_hex_str()
        issuer_remainder = self.card_tag_map['92'].value if self.card_tag_map['92'] else None
        issuer_exponent = self.card_tag_map['9F32'].value
        issuer_certificate = IssuerCertificate(unsigned_issuer_certificate, issuer_exponent, issuer_remainder)
        issuer_certificate.validate(pan)
        return issuer_certificate

    @request_card_connection
    def run_combined_data_authentication(self):
        pass

    @request_card_connection
    @request_tag_map
    def run_offline_data_authentication(self) -> bool:
        assert self.card_tag_map is not None
        assert self.chosen_application is not None
        aip_bit_map = Converter().set_hex_str(self.current_gpo_info.aip).get_as_bin_str()
        if aip_bit_map[1] == '1':
            self.run_static_data_authentication()
        elif aip_bit_map[2] == '1':
            self.run_dynamic_data_authentication()
        elif aip_bit_map[7] == '1':
            self.run_combined_data_authentication()
        return True

    def request_card(self, timeout=None, log_apdu=True) -> Terminal:
        card_type = AnyCardType()
        card_request = CardRequest(timeout=timeout, cardType=card_type)
        self.card_service = card_request.waitforcard()
        card_connection = self.card_service.connection
        self.card_connection = EmvGenericCardConnection(card_connection, log_apdu)
        return self

    @request_card_connection
    def _get_candidate_list_from_pse(self: Terminal) -> bool:
        application = '315041592e5359532e4444463031'
        self.card_connection.select_application_by_name(Converter().set_hex_str(application).get_as_int_arr(), False)
        if not self.card_connection.last_command_was_ok():
            return False
        else:
            sfi = int(self.card_connection.get_tlv_response()['6F']['A5']['88'].value, 16)
            record = 1
            while True:
                self.card_connection.read_record(sfi, record)
                if self.card_connection.last_command_was_ok():
                    directory_entry = self.card_connection.get_tlv_response()['70']['61']
                    self.candidate_list.append(CandidateAidEntry(directory_entry))
                else:
                    break
                record += 1
            return True

    @request_card_connection
    def _get_candidate_list_from_ppse(self) -> bool:
        application = '325041592e5359532e4444463031'
        self.card_connection.select_application_by_name(Converter().set_hex_str(application).get_as_int_arr(), False)
        if not self.card_connection.last_command_was_ok():
            return False
        else:
            fci = self.card_connection.get_tlv_response()['6F']['A5']['BF0C']
            tag_counter = 1
            while True:
                directory_entry = fci[f'61:{tag_counter}']
                if directory_entry is not None:
                    self.candidate_list.append(CandidateAidEntry(directory_entry))
                else:
                    break
                tag_counter += 1
            return True

    def _get_candidate_list_from_explicit_selection(self) -> bool:
        for application in self._acceptable_aids:
            self.card_connection.select_application_by_name(Converter().set_hex_str(application.aid).get_as_int_arr(),
                                                            False)
            if self.card_connection.last_command_was_ok():
                response = self.card_connection.get_tlv_response()['6F']
                if response['84'].value == application.aid or application.partial:
                    directory_entry = response['A5']
                    self.candidate_list.append(CandidateAidEntry(directory_entry))
        return True

    @request_card_connection
    def build_candidate_list(self) -> bool:
        return (self._get_candidate_list_from_pse() or
                self._get_candidate_list_from_ppse() or
                self._get_candidate_list_from_explicit_selection()) and (self.candidate_list.sort())

    @property
    def terminal_tags(self) -> Mapping[str, TerminalTag]:
        return self._terminal_tags

    @terminal_tags.setter
    def terminal_tags(self, terminal_tags: Union[str, Mapping[str, TerminalTag]]):
        if isinstance(terminal_tags, str):
            self._terminal_tags = parse_terminal_tag_file(terminal_tags)
        else:
            self._terminal_tags = terminal_tags

    @property
    def acceptable_aids(self) -> List[TerminalAcceptableAid]:
        return self._acceptable_aids

    @acceptable_aids.setter
    def acceptable_aids(self, acceptable_aids: Union[str, List[TerminalAcceptableAid]]):
        if isinstance(acceptable_aids, str):
            self._acceptable_aids = parse_terminal_acceptable_aids(acceptable_aids)
        else:
            self._acceptable_aids = acceptable_aids

    @property
    def ca_public_keys(self) -> Mapping[str, Mapping[str, RSAPublicKey]]:
        return self._ca_public_keys

    @ca_public_keys.setter
    def ca_public_keys(self,
                       ca_public_keys: Union[str, Mapping[str, Mapping[str, RSAPublicKey]]]):
        if isinstance(ca_public_keys, str):
            self._ca_public_keys = parse_certificate_authority_public_keys(ca_public_keys)
        else:
            self._ca_public_keys = ca_public_keys
