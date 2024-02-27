import asyncio
import urllib.parse
import uuid
from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Any, TypedDict, cast

from aiohttp import ClientSession, BasicAuth

from przelewy24.channels import Channels
from przelewy24.errors import P24NotAuthorizedError, P24BadRequestError
from przelewy24.transaction import Transaction
from przelewy24.utils import get_sha384_hash

PRODUCTION_URL: str = "https://secure.przelewy24.pl/"
SANDBOX_URL: str = "https://sandbox.przelewy24.pl/"


class TransactionArgs(TypedDict, total=False):
    client: str
    address: str
    zip: str
    city: str
    phone: str
    method: int
    urlStatus: str
    timeLimit: int
    channel: Union[Channels, int]
    waitForResult: bool
    regulationAccept: bool
    shipping: int
    transferLabel: str
    cart: Dict[str, Any]
    methodRefId: str
    additional: Dict[str, Any]


@dataclass
class BLIKResponse:
    success: bool
    message: str
    error_code: Optional[int] = None
    order_id: Optional[int] = None


@dataclass
class OfflineResponse:
    order_id: int
    session_id: str
    amount: int
    statement: str
    iban: str
    iban_owner: str
    iban_owner_address: str


class P24:
    def __init__(
        self,
        *,
        merchant_id: int,
        crc: str,
        api_key: str,
        return_url: str,
        sandbox: bool = False,
        pos_id: Optional[int] = None,
    ):
        self.session = ClientSession(auth=BasicAuth(str(merchant_id), api_key))
        self.sandbox = sandbox
        self.api_key = api_key
        self.crc = crc
        self.merchant_id = merchant_id
        self.pos_id = pos_id or merchant_id
        self.base_url = SANDBOX_URL if sandbox else PRODUCTION_URL
        self.return_url = return_url

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self.session.close()

    async def close(self):
        await self.session.close()

    async def register_transaction(
        self,
        amount: int,
        currency: str,
        *,
        description: str,
        email: str,
        country: str = "PL",
        language: str = "pl",
        return_url: Optional[str] = None,
        session_id: Optional[str] = None,
        data: Optional[TransactionArgs] = None,
    ) -> Transaction:
        if data is None:
            data = TransactionArgs()
        elif data.get("channel"):
            data["channel"] = int(data["channel"])

        session_id = session_id or uuid.uuid4().hex

        json_data = {
            "merchantId": self.merchant_id,
            "posId": self.pos_id,
            "sessionId": session_id,
            "urlReturn": return_url or self.return_url,
            "amount": amount,
            "currency": currency,
            "description": description,
            "email": email,
            "country": country,
            "language": language,
            "sign": get_sha384_hash(
                {
                    "sessionId": session_id,
                    "merchantId": self.merchant_id,
                    "amount": amount,
                    "currency": currency,
                    "crc": self.crc,
                }
            ),
        }
        json_data.update(data)

        req = await self.session.post(
            self.base_url + "api/v1/transaction/register",
            json=json_data,
        )

        if req.status == 400:
            raise P24BadRequestError.from_request(req)

        if req.status == 401:
            raise P24NotAuthorizedError.from_request(req)

        js = await req.json()
        return Transaction(self, js["data"]["token"], session_id)

    async def blik_charge_by_code(
        self,
        token: str,
        blik_code: str,
        *,
        alias_value: Optional[str] = None,
        alias_label: Optional[str] = None,
        recurring: Optional[Dict[str, Any]] = None,
    ) -> BLIKResponse:
        json_data = {
            "token": token,
            "blikCode": blik_code,
        }
        if alias_value is not None:
            json_data["aliasValue"] = alias_value

        if alias_label is not None:
            json_data["aliasLabel"] = alias_label

        if recurring is not None:
            json_data["recurring"] = recurring

        req = await self.session.post(
            self.base_url + "api/v1/paymentMethod/blik/chargeByCode",
            json=json_data,
        )

        if req.status == 500:
            raise P24BadRequestError.from_request(req)

        if req.status == 401:
            raise P24NotAuthorizedError.from_request(req)

        js = await req.json()
        if "error" in js:
            return BLIKResponse(False, js["error"], error_code=js["code"])

        return BLIKResponse(True, js["data"]["message"], order_id=js["data"]["orderId"])

    async def fetch_transaction_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        req = await self.session.get(
            self.base_url
            + "api/v1/transaction/by/sessionId/"
            + urllib.parse.quote_plus(session_id),
        )

        if req.status == 400:
            raise P24BadRequestError.from_request(req)

        if req.status == 401:
            raise P24NotAuthorizedError.from_request(req)

        if req.status == 404:
            return None

        js = await req.json()
        return cast(Dict[str, Any], js["data"])

    async def register_transaction_offline(self, token: str) -> OfflineResponse:
        req = await self.session.post(
            self.base_url + "api/v1/transaction/registerOffline",
            json={"token": token},
        )

        if req.status == (400, 500):
            raise P24BadRequestError.from_request(req)

        if req.status in (401, 409):
            raise P24NotAuthorizedError.from_request(req)

        js = await req.json()
        data = js["data"]
        return OfflineResponse(
            data.get("orderId", 0),
            data.get("sessionId", ""),
            data.get("amount", 0),
            data.get("statement", ""),
            data.get("iban", ""),
            data.get("ibanOwner", ""),
            data.get("ibanOwnerAddress", ""),
        )
