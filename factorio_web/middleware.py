"""Middleware for IP allowlist checking"""

from functools import lru_cache
import ipaddress
from typing import List, Any, Optional

from litestar.types import ASGIApp, Scope, Receive, Send
from litestar.response.base import ASGIResponse

from litestar.enums import HttpMethod
from litestar.middleware import ASGIMiddleware
from litestar.connection import Request


def get_remote_address(request: Request[Any, Any, Any]) -> Optional[str]:
    return request.client.host if request.client else None


class AllowList:
    """Represents an IP allowlist"""

    def __init__(
        self, networks: List[ipaddress.IPv4Network | ipaddress.IPv6Network]
    ) -> None:
        self.networks: List[ipaddress.IPv4Network | ipaddress.IPv6Network] = networks

    @lru_cache(maxsize=1024, typed=True)
    def is_allowed(self, ip: Optional[str]) -> bool:
        """check the allowlist for an IP"""
        if not self.networks:
            return True
        if ip is None:
            return False
        try:
            ip_addr = ipaddress.ip_address(ip)
        except ValueError:
            return False
        return any(ip_addr in network for network in self.networks)


class HostLimiterMiddleware(ASGIMiddleware):
    """limits access to POST requests if there's an allowlist configured"""

    def __init__(
        self,
        allow_list: List[ipaddress.IPv4Network | ipaddress.IPv6Network],
    ) -> None:
        self.allowlist = AllowList(allow_list)

    async def handle(
        self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp
    ) -> None:
        app = scope["litestar_app"]
        request: Request[Any, Any, Any] = app.request_class(scope)
        if request.method == HttpMethod.POST:
            client_host = get_remote_address(request)
            if not self.allowlist.is_allowed(client_host):
                response = ASGIResponse(body="Access denied", status_code=403)
                await response(scope, receive, send)
                return
        await next_app(scope, receive, send)
