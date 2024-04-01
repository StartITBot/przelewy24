from pprint import pprint

from decimal import Decimal

import urllib.parse
import uuid
from aiohttp import ClientSession, BasicAuth
from typing import Optional, Union, Dict, Any, TypedDict, cast

from przelewy24.blikresponse import BLIKResponse
from przelewy24.channels import Channels
from przelewy24.errors import P24NotAuthorizedError, P24BadRequestError
from przelewy24.offlineresponse import OfflineResponse
from przelewy24.transactiondataresponse import TransactionDataResponse
from przelewy24.transactioncreateresponse import TransactionCreateResponse
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


class NULL:
    pass


def fill_null(**kwargs) -> Dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not NULL}


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

    # noinspection PyShadowingBuiltins
    async def create_transaction(
        self,
        amount: Union[Decimal, int],
        currency: str,
        *,
        description: str,
        email: str,
        country: str = "PL",
        language: str = "pl",
        return_url: Optional[str] = None,
        session_id: Optional[str] = None,
        data: Optional[TransactionArgs] = None,
        client: str = NULL,
        address: str = NULL,
        zip: str = NULL,
        city: str = NULL,
        phone: str = NULL,
        method: int = NULL,
        url_status: str = NULL,
        time_limit: int = NULL,
        channel: Union[Channels, int] = NULL,
        wait_for_result: bool = NULL,
        regulation_accept: bool = NULL,
        shipping: int = NULL,
        transfer_label: str = NULL,
        cart: Dict[str, Any] = NULL,
        method_ref_id: str = NULL,
        additional: Dict[str, Any] = NULL,
    ) -> TransactionCreateResponse:
        if data is None:
            data = TransactionArgs()
        elif data.get("channel"):
            data["channel"] = int(data["channel"])

        session_id = session_id or uuid.uuid4().hex

        if isinstance(amount, Decimal):
            amount = int(amount * 100)

        sign = get_sha384_hash(
            {
                "sessionId": session_id,
                "merchantId": self.merchant_id,
                "amount": amount,
                "currency": currency,
                "crc": self.crc,
            }
        )

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
            "sign": sign,
            **fill_null(
                client=client,
                address=address,
                zip=zip,
                city=city,
                phone=phone,
                method=method,
                urlStatus=url_status,
                timeLimit=time_limit,
                channel=channel,
                waitForResult=wait_for_result,
                regulationAccept=regulation_accept,
                shipping=shipping,
                transferLabel=transfer_label,
                cart=cart,
                methodRefId=method_ref_id,
                additional=additional,
            ),
        }
        json_data.update(data)

        req = await self.session.post(
            self.base_url + "api/v1/transaction/register",
            json=json_data,
        )

        if req.status == 400:
            js = await req.json()
            raise P24BadRequestError.from_request(req, js)

        if req.status == 401:
            js = await req.json()
            raise P24NotAuthorizedError.from_request(req, js)

        js = await req.json()
        return TransactionCreateResponse(
            token=js["data"]["token"], session_id=session_id, sign=sign, _base=self
        )

    async def verify_transaction(
        self, amount: int, currency: str, *, session_id: str, order_id: int
    ):
        sign = get_sha384_hash(
            {
                "sessionId": session_id,
                "orderId": order_id,
                "amount": amount,
                "currency": currency,
                "crc": self.crc,
            }
        )

        json_data = {
            "merchantId": self.merchant_id,
            "posId": self.pos_id,
            "sessionId": session_id,
            "amount": amount,
            "currency": currency,
            "orderId": order_id,
            "sign": sign,
        }

        req = await self.session.put(
            self.base_url + "api/v1/transaction/verify",
            json=json_data,
        )

        if req.status == 400:
            js = await req.json()
            raise P24BadRequestError.from_request(req, js)

        if req.status == 401:
            js = await req.json()
            raise P24NotAuthorizedError.from_request(req, js)

        return await req.json()

    async def charge_blik_by_code(
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
            "blikCode": blik_code.replace(" ", "").replace("\n", ""),
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
            js = await req.json()
            raise P24BadRequestError.from_request(req, js)

        if req.status == 401:
            js = await req.json()
            raise P24NotAuthorizedError.from_request(req, js)

        js = await req.json()
        if "error" in js:
            return BLIKResponse(False, js["error"], error_code=js["code"])

        return BLIKResponse(True, js["data"]["message"], order_id=js["data"]["orderId"])

    async def fetch_transaction_data(
        self, session_id: str
    ) -> Optional[TransactionDataResponse]:
        req = await self.session.get(
            self.base_url
            + "api/v1/transaction/by/sessionId/"
            + urllib.parse.quote_plus(session_id),
        )

        if req.status == 400:
            js = await req.json()
            raise P24BadRequestError.from_request(req, js)

        if req.status == 401:
            js = await req.json()
            raise P24NotAuthorizedError.from_request(req, js)

        if req.status == 404:
            return None

        js = await req.json()

        data = js["data"]
        return TransactionDataResponse(
            statement=data.get("statement", ""),
            order_id=data.get("orderId", 0),
            session_id=data.get("sessionId", ""),
            status=data.get("status", 0),
            amount=data.get("amount", 0),
            currency=data.get("currency", ""),
            date=data.get("date", ""),
            date_of_transaction=data.get("dateOfTransaction", ""),
            client_email=data.get("clientEmail", ""),
            account_md5=data.get("accountMD5", ""),
            payment_method=data.get("paymentMethod", 0),
            description=data.get("description", ""),
            client_name=data.get("clientName", ""),
            client_address=data.get("clientAddress", ""),
            client_city=data.get("clientCity", ""),
            client_postcode=data.get("clientPostcode", ""),
            batch_id=data.get("batchId", 0),
            fee=data.get("fee", ""),
            _base=self,
        )

    async def register_transaction_offline(self, token: str) -> OfflineResponse:
        req = await self.session.post(
            self.base_url + "api/v1/transaction/registerOffline",
            json={"token": token},
        )

        if req.status == (400, 500):
            js = await req.json()
            raise P24BadRequestError.from_request(req, js)

        if req.status in (401, 409):
            js = await req.json()
            raise P24NotAuthorizedError.from_request(req, js)

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
