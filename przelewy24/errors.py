from typing import Dict, Any

from aiohttp import ClientResponseError, ClientResponse


class P24Error(Exception):
    pass


class P24ClientError(ClientResponseError, P24Error):
    def __init__(self, *args, **kwargs):
        self.json = kwargs.pop("json", None)
        super().__init__(*args, **kwargs)

    @classmethod
    def from_request(cls, req: ClientResponse, js: Dict[str, Any]) -> "P24ClientError":
        return cls(
            req.request_info,
            req.history,
            status=req.status,
            message=req.reason,
            headers=req.headers,
            json=js,
        )

    def __str__(self) -> str:
        return "{} {} on {} {} (data: {!r})".format(
            self.status,
            self.message,
            self.request_info.method,
            self.request_info.real_url,
            self.json,
        )


class P24BadRequestError(P24ClientError):
    pass


class P24NotAuthorizedError(P24ClientError):
    pass
