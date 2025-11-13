"""Middleware for IP allowlist checking"""

from litestar.middleware.base import AbstractMiddleware, DefineMiddleware
from dataclasses import dataclass, field
import ipaddress

from litestar.types import ASGIApp, Scope, Receive, Send
from litestar.response.base import ASGIResponse

from litestar.enums import ScopeType, HttpMethod

from litestar.connection import Request
from typing import List, Any


def get_remote_address(request: Request[Any, Any, Any]) -> str:
    return request.client.host if request.client else "127.0.0.1"


class HostLimiterMiddleware(AbstractMiddleware):
    def __init__(self, app: ASGIApp, config: "HostLimiter") -> None:
        """Initialize ``RateLimitMiddleware``."""
        super().__init__(
            app=app,
            exclude=config.exclude,
            scopes={ScopeType.HTTP},
        )
        self.allowlist: List[ipaddress.IPv4Network | ipaddress.IPv6Network] = (
            config.allowlist
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
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
        await self.app(scope, receive, send)


@dataclass
class HostLimiter:
    allowlist: List[ipaddress.IPv4Network | ipaddress.IPv6Network] = field(
        default_factory=list
    )
    middleware_class: type[HostLimiterMiddleware] = field(default=HostLimiterMiddleware)
    exclude: str | list[str] | None = field(default=None)

    @property
    def middleware(self) -> DefineMiddleware:
        return DefineMiddleware(self.middleware_class, config=self)
