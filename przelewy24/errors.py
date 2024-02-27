from aiohttp import ClientResponseError


class P24Error(Exception):
    pass


class P24ClientError(ClientResponseError, P24Error):
    @classmethod
    def from_request(cls, req):
        return cls(
            req.request_info,
            req.history,
            status=req.status,
            message=req.reason,
            headers=req.headers,
        )


class P24BadRequestError(P24ClientError):
    pass


class P24NotAuthorizedError(P24ClientError):
    pass
