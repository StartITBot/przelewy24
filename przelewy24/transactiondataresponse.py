import datetime
from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING, Optional, Union, Dict, Literal

from .paymentmethod import PaymentMethod

if TYPE_CHECKING:
    from .api import P24


class TransactionStatus(IntEnum):
    NO_PAYMENT = 0
    ADVANCE_PAYMENT = 1
    PAYMENT_MADE = 2
    PAYMENT_RETURNED = 3


@dataclass
class TransactionDataResponse:
    statement: str
    order_id: int
    session_id: str
    status: TransactionStatus
    amount: int
    currency: str
    date: Optional[datetime.datetime]
    date_of_transaction: Optional[datetime.datetime]
    client_email: str
    account_md5: str
    payment_method: Union[PaymentMethod, int]
    description: str
    client_name: str
    client_address: str
    client_city: str
    client_postcode: str
    batch_id: int
    fee: int

    _base: "Optional[P24]" = field(repr=False, hash=False, compare=False, default=None)

    async def verify(self) -> Literal[True]:
        assert self._base is not None, "Base is not set"
        return await self._base.verify_transaction(
            self.amount,
            self.currency,
            session_id=self.session_id,
            order_id=self.order_id,
        )

    def __post_init__(self) -> None:
        """
        Post init method to convert some API fields to proper types
        """

        self.status = TransactionStatus(self.status)

        if isinstance(self.date, str):
            self.date = (
                datetime.datetime.strptime(self.date, "%Y%m%d%H%M")
                if self.date
                else None
            )

        if isinstance(self.date_of_transaction, str):
            self.date_of_transaction = (
                datetime.datetime.strptime(self.date_of_transaction, "%Y%m%d%H%M")
                if self.date_of_transaction
                else None
            )

        if isinstance(self.fee, str):
            self.fee = int(self.fee)

        if isinstance(self.payment_method, int):
            if PaymentMethod.exists(self.payment_method):
                self.payment_method = PaymentMethod(self.payment_method)

    def to_dict(
        self,
    ) -> Dict[str, Union[str, int, TransactionStatus, PaymentMethod, None]]:
        return {
            "statement": self.statement,
            "order_id": self.order_id,
            "session_id": self.session_id,
            "status": self.status,
            "amount": self.amount,
            "currency": self.currency,
            "date": self.date.isoformat() if self.date else None,
            "date_of_transaction": (
                self.date_of_transaction.isoformat()
                if self.date_of_transaction
                else None
            ),
            "client_email": self.client_email,
            "account_md5": self.account_md5,
            "payment_method": self.payment_method,
            "description": self.description,
            "client_name": self.client_name,
            "client_address": self.client_address,
            "client_city": self.client_city,
            "client_postcode": self.client_postcode,
            "batch_id": self.batch_id,
            "fee": self.fee,
        }
