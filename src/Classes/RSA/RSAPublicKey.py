class RSAPublicKey:

    def __init__(self, modulus: int, exponent: int):
        self.modulus = modulus
        self.exponent = exponent

    def encrypt(self, msg: int):
        return pow(msg, self.exponent, self.modulus)

    def decrypt(self, msg: int):
        return pow(msg, self.exponent, self.modulus)

    @property
    def modulus(self) -> int:
        return self._modulus

    @modulus.setter
    def modulus(self, modulus: int):
        self._modulus = modulus

    @property
    def exponent(self) -> int:
        return self._exponent

    @exponent.setter
    def exponent(self, exponent: int):
        self._exponent = exponent
