from dataclasses import dataclass, field
from typing import Optional

from src.Classes.Converter import Converter
from src.Classes.RSA.RSAPublicKey import RSAPublicKey
from src.Util import get_n_bytes


@dataclass
class CertificateModulus:
    full_pk: str = field(repr=False)
    pk_len: int
    exponent: str
    remainder: Optional[str]
    padding: str = field(init=False)
    modulus: str = field(init=False)
    rsa_key: RSAPublicKey = field(init=False)

    def __post_init__(self):
        if self.pk_len >= len(self.full_pk) // 2:
            self.modulus = self.full_pk + (self.remainder if self.remainder else None)
            self.padding = ''
        else:
            self.modulus, self.padding = get_n_bytes(self.full_pk, self.pk_len)
        exponent = Converter().set_hex_str(self.exponent).get_as_int()
        modulus = Converter().set_hex_str(self.modulus).get_as_int()
        self.rsa_key = RSAPublicKey(exponent=exponent, modulus=modulus)
