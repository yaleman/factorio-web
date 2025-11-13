"""Middleware for IP allowlist checking"""

import ipaddress

from litestar.types import ASGIApp, Scope, Receive, Send
from litestar.response.base import ASGIResponse

from litestar.enums import HttpMethod
from litestar.middleware import ASGIMiddleware
from litestar.connection import Request
from typing import List, Any


def get_remote_address(request: Request[Any, Any, Any]) -> str:
    return request.client.host if request.client else "127.0.0.1"


class HostLimiterMiddleware(ASGIMiddleware):
    def __init__(
        self,
        allow_list: List[ipaddress.IPv4Network | ipaddress.IPv6Network],
    ) -> None:
        self.allowlist: List[ipaddress.IPv4Network | ipaddress.IPv6Network] = allow_list

    async def handle(
        self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp
    ) -> None:
        app = scope["litestar_app"]
        request: Request[Any, Any, Any] = app.request_class(scope)
        if request.method == HttpMethod.POST:
            client_host = get_remote_address(request)
            if self.allowlist and not any(
                ipaddress.ip_address(client_host) in network
                for network in self.allowlist
            ):
                response = ASGIResponse(body="Access denied", status_code=403)
                await response(scope, receive, send)
                return
        await next_app(scope, receive, send)
