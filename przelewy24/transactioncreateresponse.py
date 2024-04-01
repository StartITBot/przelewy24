from dataclasses import dataclass, field

from typing import TYPE_CHECKING, Optional, Dict

if TYPE_CHECKING:
    from .api import P24
    from .blikresponse import BLIKResponse
    from .transactiondataresponse import TransactionDataResponse
    from .offlineresponse import OfflineResponse


@dataclass
class TransactionCreateResponse:
    token: str
    session_id: str
    sign: str

    _base: Optional["P24"] = field(repr=False, hash=False, compare=False, default=None)

    async def fetch_data(self) -> "Optional[TransactionDataResponse]":
        assert self._base is not None, "Base is not set"
        return await self._base.fetch_transaction_data(self.session_id)

    async def register_offline(self) -> "OfflineResponse":
        assert self._base is not None, "Base is not set"
        return await self._base.register_transaction_offline(self.token)

    @property
    def url(self) -> str:
        assert self._base is not None, "Base is not set"
        return f"{self._base.base_url}trnRequest/{self.token}"

    async def charge_blik_by_code(self, blik_code: str) -> "BLIKResponse":
        assert self._base is not None, "Base is not set"
        return await self._base.charge_blik_by_code(self.token, blik_code)

    def to_dict(self) -> Dict[str, str]:
        return {
            "token": self.token,
            "session_id": self.session_id,
        }
