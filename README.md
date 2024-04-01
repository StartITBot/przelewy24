# przelewy24

work in progress async python lib for przelewy24 api

## Project status
development phase, updates can contain breaking changes (!)

## Basic usage
```python
from aiohttp import web
from uuid import uuid4
import przelewy24 as p24

async def create_payment():
    # Random string to identify the transaction
    session_id = uuid4().hex
    
    async with p24.P24(
        merchant_id=0,
        crc='',
        api_key='',
        return_url=f"https://example.com/return?session_id={session_id}",
        sandbox=False,
    ) as client:
        trans: p24.TransactionCreateResponse = await client.create_transaction(
            150_00,
            "PLN",
            description="Test transaction",
            email="test@example.com",
            session_id=session_id
        )
    
    raise web.HTTPFound(trans.url)


async def check_status(request: web.Request):
    session_id = request.query.get("session_id")
    
    async with p24.P24(
        merchant_id=0,
        crc='',
        api_key='',
        return_url='',
        sandbox=False,
    ) as client:
        transaction_data = await client.fetch_transaction_data(session_id)
        if not transaction_data:
            raise web.HTTPBadRequest(text="Invalid session_id")
    
        if transaction_data.status == p24.TransactionStatus.NO_PAYMENT:
            raise web.HTTPBadRequest(text="No payment was made.")
        
        if transaction_data.status == p24.TransactionStatus.PAYMENT_MADE:
            raise web.HTTPBadRequest(text="You have already paid for this transaction.")
        
        if transaction_data.status == p24.TransactionStatus.PAYMENT_RETURNED:
            raise web.HTTPBadRequest(text="Payment was refunded.")
        
        try:
            await transaction_data.verify()
        except p24.P24BadRequestError:
            raise web.HTTPBadRequest(reason="Error: Cannot verify payment")
        
        # Remember to check if transaction_data.amount is equal to the amount you expect
    
    return web.Response(text="Payment successful")

```