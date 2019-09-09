# coding=utf-8
from __future__ import annotations

from typing import List, Optional

from smartcard import CardConnection
from smartcard.sw.SWExceptions import WarningProcessingException

from .ConnectionObserverWrapper import ConnectionObserverWrapper
from .ErrorChainWrapper import ErrorChainWrapper


class GenericCardConnection:
    """CardConnection with default ErrorChain and Observer"""

    def __init__(self, card_connection: CardConnection):
        self.connection = None
        self.build_connection(card_connection)
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
                   le: Optional[int] = None) -> GenericCardConnection:
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

    def build_connection(self, card_connection):
        self.connection = card_connection
        self.connection.setErrorCheckingChain(ErrorChainWrapper)
        observer = ConnectionObserverWrapper()
        self.connection.addObserver(observer)
        self.connection.addSWExceptionToFilter(WarningProcessingException)
        self.connection.connect()

    def send(self, apdu_array: Optional[List[int]] = None) -> GenericCardConnection:
        if apdu_array is None:
            apdu_array = self.final_apdu
        self.response, self.sw1, self.sw2 = self.connection.transmit(apdu_array)
        if self.sw1 == 0x61:
            self.get_data()
        if self.sw1 == 0x6C:
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
