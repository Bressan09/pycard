from __future__ import annotations
from typing import List, Optional, Tuple

from smartcard import CardConnection
from smartcard.sw.SWExceptions import WarningProcessingException

from .ConnectionObserverWrapper import ConnectionObserverWrapper
from .ErrorChainWrapper import ErrorChainWrapper
from ..Classes.Converter import Converter
from ..Classes.EmvTag import EmvTag
from ..Classes.TlvBuilder import TlvBuilder
from ..Classes.TlvParser import TlvParser
from ..Convert import convert_sfi_to_param2


class EmvGenericCardConnection:
    """CardConnection with default ErrorChain and Observer"""

    def __init__(self, card_connection: CardConnection, log_apdu=True):
        self.connection = None
        self.build_connection(card_connection, log_apdu)
        self.final_apdu = []
        self.response = []
        self.sw1 = []
        self.sw2 = []

    def build_apdu(self,
                   cla: int,
                   ins: int,
                   p1: int,
                   p2: int,
                   lc: Optional[int] = None,
                   data: Optional[List[int]] = None,
                   le: int = 0x00) -> EmvGenericCardConnection:
        final_apdu = [cla, ins, p1, p2]
        lc = lc
        data = data
        le = le

        if data is not None:
            if lc is not None:
                if len(data) != lc:
                    raise ValueError(f'Data Length {len(data)} '
                                     f'does not match LC - {lc}')
            else:
                lc = len(data)
            final_apdu.append(lc)
            final_apdu += data
        else:
            if lc is not None:
                ValueError('When using LC the Data must be provided')

        if le is not None:
            final_apdu.append(le)
        self.final_apdu = final_apdu
        return self

    def last_command_was_ok(self) -> bool:
        return self.get_sw_array() == (0x90, 0x00)

    def get_tlv_response(self) -> Optional[EmvTag]:
        if self.last_command_was_ok():
            return TlvParser().parse(self.response)
        return None

    def get_processing_options(self, pdol_value: str):
        final_hex_pdol = TlvBuilder().append_hex_str_value(pdol_value).get_tlv('83')
        final_pdol = Converter().set_hex_str(final_hex_pdol).get_as_int_arr()
        self.build_apdu(cla=0x80,
                        ins=0xA8,
                        p1=0x00,
                        p2=0x00,
                        data=final_pdol,
                        le=0x00).send()

    def internal_authenticate(self, random_number: str):
        random_number = Converter().set_hex_str(random_number).get_as_int_arr()
        self.build_apdu(cla=0x00,
                        ins=0x88,
                        p1=0x00,
                        p2=0x00,
                        data=random_number,
                        le=0x00).send()

    def select_application_by_name(self, application_name, next_ocurrence=False) -> EmvGenericCardConnection:
        p2 = 0x02 if next_ocurrence else 0x00
        self.build_apdu(cla=0x00,
                        ins=0xA4,
                        p1=0x04,
                        p2=p2,
                        data=application_name).send()
        return self

    def read_record(self, sfi: int, record: int) -> EmvGenericCardConnection:
        sfi_p2 = convert_sfi_to_param2(sfi)
        self.build_apdu(cla=0x00,
                        ins=0xB2,
                        p1=record,
                        p2=sfi_p2).send()
        return self

    def get_sw_array(self) -> Tuple[int, int]:
        return self.sw1, self.sw2

    def build_connection(self, card_connection: CardConnection, log_apdu: bool):
        self.connection = card_connection
        #self.connection.setErrorCheckingChain(ErrorChainWrapper)
        if log_apdu:
            observer = ConnectionObserverWrapper()
            self.connection.addObserver(observer)
        self.connection.addSWExceptionToFilter(WarningProcessingException)
        self.connection.connect()

    def send(self, apdu_array: Optional[List[int]] = None) -> EmvGenericCardConnection:
        if apdu_array is None:
            apdu_array = self.final_apdu
        self.response, self.sw1, self.sw2 = self.connection.transmit(apdu_array)
        if self.sw1 == 0x61:
            self.get_data()
        if self.sw1 == 0x6C:
            apdu_array = apdu_array[:-1]
            apdu_array.append(self.sw2)
            self.send(apdu_array)
        return self

    def get_data(self) -> None:
        self.build_apdu(cla=0x00, ins=0xC0, p1=0x00, p2=0x00, le=self.sw2).send()

    def disconnect(self):
        self.connection.disconnect()

    @property
    def connection(self) -> CardConnection:
        return self._connection

    @connection.setter
    def connection(self, connection: CardConnection):
        self._connection = connection

    @property
    def response(self) -> List[int]:
        return self._response

    @response.setter
    def response(self, response: List[int]):
        self._response = response

    @property
    def sw1(self) -> int:
        return self._sw1

    @sw1.setter
    def sw1(self, sw1: int):
        self._sw1 = sw1

    @property
    def sw2(self) -> int:
        return self._sw2

    @sw2.setter
    def sw2(self, sw2: int):
        self._sw2 = sw2
