# coding=utf-8


# noinspection PyUnusedClass
class RSAPrivateKey:

    def __init__(self, p: int, q: int):
        self.p = p
        self.q = q
        self.phi = self.generate_phi()
        self.k = 2  # random.randint(1, 10)
        self.d = self.generate_d()

    def generate_phi(self):
        return (self.p - 1) * (self.q - 1)

    def generate_d(self):
        return ((self.k * self.phi) + 1) // 3

    def decrypt(self, msg: int):
        return pow(msg, self.d, self.p * self.q)

    def encrypt(self, msg: int):
        return pow(msg, self.d, self.p * self.q)
