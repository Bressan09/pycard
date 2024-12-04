
from typing import Optional

from src.Classes.Certificates.Certificate import Certificate


class IssuerCertificate(Certificate):

    def __post_init__(self, remainder: Optional[str]):
        super().parse_fields(4, 36, remainder)

    def validate(self, card_pan: str):
        # The Recovered Data Trailer is equal to 'BC'
        assert self.trailer == 'BC'

        # The Recovered Data Header is equal to '6A'
        assert self.header == '6A'

        # The Certificate Format is equal to '02'
        assert self.format == '02'

        # Concatenation of Certificate Format through Issuer Public Key or Leftmost Digits of the Issuer Public Key,
        #          followed by the Issuer Public Key Remainder (if present), and the Issuer Public Key Exponent
        remainder = self.pk.remainder if self.pk.remainder else ''
        self.validate_hash(remainder + self.exponent)

        # Verify that the Issuer Identifier matches the lefmost 3-8 PAN digits
        self.validate_pan_identifier(card_pan, min_size=3)
