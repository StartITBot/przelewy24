from enum import IntEnum


class PaymentMethod(IntEnum):
    SANTANDER = 20
    INTELIGO = 26
    PKO_BP = 31
    BPH = 35
    CREDIT_AGRICOLE = 45
    TOYOTA_BANK = 64
    PEKAO = 65
    GET_BANK = 68
    VOLKSWAGEN_BANK = 69
    POLBANK = 82
    MILLENNIUM = 85
    ALIOR_BANK = 88
    EUROBANK = 94
    BOS = 99
    RAIFFEISEN_POLBANK = 102
    DNB_NORD = 103
    E_SKOK = 105
    PAYSAFECARD = 107
    DEUTSCHE_BANK = 110
    ING = 112
    CITI_HANDLOWY = 119
    ALIOR_RATY = 129
    PLUS_BANK = 131
    IKO = 135
    MBANK_RATY = 136
    POCZTOWY24 = 141
    BANKI_SPOLDZIELCZE = 143
    BANK_NOWY = 144
    VELO_BANK = 153
    BLIK = 154
    PRZEKAZ_TRADYCYJNY = 178
    BLIK_1CLICK = 181
    T_MOBILE_USLUGI_BANKOWE = 121
    NEST_PRZELEW = 222
    BNP_PARIBAS = 223
    MBANK_MTRANSFER = 243
    MBANK_ITP = 270
    ING_ITP = 271
    PKO_BP_ITP = 274
    INTELIGO_ITP = 279
    KASA_STEFCZYKA = 292

    @classmethod
    def exists(cls, value: int) -> bool:
        return value in cls.__members__.values()
