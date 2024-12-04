import hashlib
from abc import abstractmethod
from dataclasses import dataclass, field, InitVar
from typing import Optional

from src.Classes.CertificateModulus import CertificateModulus
from src.Classes.Converter import Converter
from src.Classes.RSA.RSAPublicKey import RSAPublicKey
from src.Util import get_n_bytes


@dataclass
class Certificate:
    header: str = field(init=False)
    format: str = field(init=False)
    identifier: str = field(init=False)
    expiration_date: str = field(init=False)
    serial_number: str = field(init=False)
    hash_algorithm: str = field(init=False)
    pk_algorithm: str = field(init=False)
    pk_length: str = field(init=False)
    pk_exponent_length: str = field(init=False)
    pk: CertificateModulus = field(init=False)
    hash_result: str = field(init=False)
    trailer: str = field(init=False)
    hashable_list: str = field(init=False)
    full_certificate: str = field(repr=False)
    exponent: str
    remainder: InitVar[Optional[str]]

    @abstractmethod
    def __post_init__(self, remainder: Optional[str]):
        pass

    def parse_fields(self, identifier_len: int, metadata_len: int, remainder: Optional[str]):
        ca_len = len(self.full_certificate) // 2
        self.hashable_list = ''
        self.header, remaining = get_n_bytes(self.full_certificate, 1)
        self.format, remaining = get_n_bytes(remaining, 1)
        self.hashable_list += self.format
        self.identifier, remaining = get_n_bytes(remaining, identifier_len)
        self.hashable_list += self.identifier
        self.expiration_date, remaining = get_n_bytes(remaining, 2)
        self.hashable_list += self.expiration_date
        self.serial_number, remaining = get_n_bytes(remaining, 3)
        self.hashable_list += self.serial_number
        self.hash_algorithm, remaining = get_n_bytes(remaining, 1)
        self.hashable_list += self.hash_algorithm
        self.pk_algorithm, remaining = get_n_bytes(remaining, 1)
        self.hashable_list += self.pk_algorithm
        self.pk_length, remaining = get_n_bytes(remaining, 1)
        self.hashable_list += self.pk_length
        self.pk_exponent_length, remaining = get_n_bytes(remaining, 1)
        self.hashable_list += self.pk_exponent_length
        full_pk, remaining = get_n_bytes(remaining, ca_len - metadata_len)
        self.hashable_list += full_pk
        int_pk_length = Converter().set_hex_str(self.pk_length).get_as_int()
        self.pk = CertificateModulus(full_pk, int_pk_length, self.exponent, remainder)
        self.hash_result, remaining = get_n_bytes(remaining, 20)
        self.trailer, remaining = get_n_bytes(remaining, 1)

    def get_as_public_key(self) -> RSAPublicKey:
        return self.pk.rsa_key

    @staticmethod
    def get_sha1(hashable_list: str) -> str:
        return hashlib.sha1(bytes.fromhex(hashable_list)).hexdigest().upper()

    def validate_hash(self, additional_info: str):
        assert self.hash_result == self.get_sha1(self.hashable_list + additional_info)

    def validate_pan_identifier(self, card_pan: str, min_size: int):
        identifier_trimmed = self.identifier.strip('F')
        assert len(identifier_trimmed) >= min_size and card_pan.startswith(identifier_trimmed)
