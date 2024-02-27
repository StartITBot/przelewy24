from enum import IntEnum


class Channels(IntEnum):
    CARDS_APPLEPAY_GOOGLEPAY = 1
    TRANSFERS = 2
    TRADITIONAL_TRANSFER = 4
    ALL_24_7 = 16
    USE_PREPAYMENT = 32
    PAY_BY_LINK = 64
    INSTALLMENTS = 128
    WALLETS = 256
    CARDS = 4096
    BLIK = 8192
    ALL_EXCEPT_BLIK = 16384

    def __add__(self, other):
        return self.value | other.value

    def __sub__(self, other):
        return self.value & ~other.value
