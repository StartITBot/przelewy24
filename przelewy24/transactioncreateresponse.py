from dataclasses import dataclass, field, asdict

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from przelewy24.api import P24
    from przelewy24.blikresponse import BLIKResponse
    from przelewy24.transactiondataresponse import TransactionDataResponse
    from przelewy24.offlineresponse import OfflineResponse


@dataclass
class TransactionCreateResponse:
    token: str
    session_id: str
    sign: str

    _base: "Optional[P24]" = field(repr=False, hash=False, compare=False, default=None)

    async def fetch_data(self) -> "Optional[TransactionDataResponse]":
        return await self._base.fetch_transaction_data(self.session_id)

    async def register_offline(self) -> "OfflineResponse":
        return await self._base.register_transaction_offline(self.token)

    @property
    def url(self):
        return f"{self._base.base_url}trnRequest/{self.token}"

    async def charge_blik_by_code(self, blik_code: str) -> "BLIKResponse":
        return await self._base.charge_blik_by_code(self.token, blik_code)

    def to_dict(self):
        return {
            "token": self.token,
            "session_id": self.session_id,
        }
