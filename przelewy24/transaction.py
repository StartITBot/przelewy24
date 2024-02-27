from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from przelewy24.api import P24, BLIKResponse


# noinspection PyProtectedMember
class Transaction:
    def __init__(self, base: "P24", token: str, session: str):
        self.base = base
        self.token = token
        self.session = session

    async def fetch_data(self):
        return await self.base.fetch_transaction_data(self.session)

    async def register_offline(self):
        return await self.base.register_transaction_offline(self.token)

    async def blik_charge_by_code(self, blik_code: str) -> "BLIKResponse":
        return await self.base.blik_charge_by_code(self.token, blik_code)
