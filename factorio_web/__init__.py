import os
from pathlib import Path
from typing import Annotated, List, Any
import re
import ipaddress
import sys

from litestar import Litestar, get, MediaType, post, Response
from litestar.connection import Request
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.exceptions import HTTPException, ValidationException
from litestar.logging import LoggingConfig
from litestar.response.redirect import ASGIRedirectResponse
from pydantic import BaseModel, ValidationError


from .models import PlayerInfo, PlayersInfo, UptimeResponse, SaveForm, RconCommand
from .rcon_command import run_command
from .config import Settings
from .middleware import HostLimiterMiddleware

MY_PATH = os.path.dirname(__file__)

try:
    CONFIG = Settings.model_validate({})
except ValidationError as e:
    print("Configuration error:", e)
    sys.exit(1)
    # raise e

# Parse allowlist on startup using the Settings method
ALLOWLIST = CONFIG.allowlist()


class IndexQuery(BaseModel):
    saved: bool | None = None
    filename: str | None = None


@get("/", media_type=MediaType.HTML)
async def index_html(
    request: Request[Any, Any, Any], query: IndexQuery
) -> str:  # type : ignore[type-arg]
    if not CONFIG.allowlist():
        index_file = "index-admin.html"
    for network in ALLOWLIST:
        if request.client and network.overlaps(
            ipaddress.ip_network(request.client.host)
        ):
            index_file = "index-admin.html"
            with open(os.path.join(MY_PATH, "static", index_file), "r") as f:
                contents = f.read()
                if query.saved:
                    contents = contents.replace(
                        "<!-- SAVED_NOTICE -->",
                        '<div class="notice" id="message">Game saved successfully{}</div>'.format(
                            f" as {query.filename}." if query.filename else "."
                        ),
                    )
                return contents
            break
    else:
        index_file = "index-nonadmin.html"
        with open(os.path.join(MY_PATH, "static", index_file), "r") as f:
            return f.read()


@get("/static/{filename:str}")
async def static_file(filename: str) -> Response[str | bytes]:
    if (
        filename.lower().startswith("..")
        or "/" in filename
        or "\\" in filename
        or ".htm" in filename
    ):
        raise HTTPException(status_code=400, detail="Invalid filename.")
    filepath = Path(os.path.join(MY_PATH, "static", filename))
    try:
        if filepath.exists() and filepath.is_file():
            if filepath.suffix == ".css":
                return Response(
                    filepath.read_text(encoding="utf-8"), media_type=MediaType.CSS
                )
            elif filepath.suffix == ".js":
                return Response(
                    filepath.read_text(encoding="utf-8"),
                    media_type="application/javascript",
                )
            return Response(filepath.read_bytes())
        print("File not found:", filename)
        raise HTTPException(status_code=404, detail=f"File {filename} not found.")
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        raise e


@get("/players", media_type=MediaType.JSON)
async def list_players() -> PlayersInfo:
    response = await run_command(["/players"], CONFIG)
    lines = response.splitlines()
    player_count = lines[0].split("(")[1].split(")")[0]
    players = {}
    for line in lines[1:]:
        if line.strip() == "":
            continue
        parts = line.strip().split()
        name = parts[0]
        online = "(online)" in parts
        players[name] = {"online": online, "name": parts[0]}
    return PlayersInfo.model_validate({"count": player_count, "players": players})


@get("/seed", media_type=MediaType.JSON)
async def get_seed() -> int:
    response = await run_command(["/seed"], CONFIG)
    return int(response.strip())


@get("/uptime", media_type=MediaType.JSON)
async def get_uptime() -> dict[str, int]:
    response = (await run_command(["/time"], CONFIG)).strip()
    hour_regex = re.compile(r"(\d+)\s+hours?")
    minute_regex = re.compile(r"(\d+)\s+minutes?")
    second_regex = re.compile(r"(\d+)\s+seconds?")
    hours_match = hour_regex.search(response)
    minutes_match = minute_regex.search(response)
    seconds_match = second_regex.search(response)
    data = {
        "hours": int(hours_match.group(1)) if hours_match else None,
        "minutes": int(minutes_match.group(1)) if minutes_match else None,
        "seconds": int(seconds_match.group(1)) if seconds_match else None,
    }

    return UptimeResponse.model_validate(data).model_dump(exclude_none=True)


@get("/admins", media_type=MediaType.JSON)
async def list_admins() -> List[PlayerInfo]:
    response = await run_command(["/admins"], CONFIG)
    lines = response.splitlines()
    admins = []
    for line in lines:
        if line.strip() == "":
            continue
        parts = line.strip().split()
        name = parts[0]
        admins.append(PlayerInfo(name=name, online="(online)" in parts))
    return admins


@post("/shutdown", media_type=MediaType.JSON)
async def shutdown_server() -> str:
    response = await run_command(["/quit"], CONFIG)
    return '"{}"'.format(response.strip())


@post("/save", media_type=MediaType.JSON)
async def save_game(
    data: Annotated[SaveForm, Body(media_type=RequestEncodingType.URL_ENCODED)],
) -> ASGIRedirectResponse:
    command = ["/save"]
    if data is not None and data.filename is not None and data.filename.strip() != "":
        command.append(data.filename)
    response = (await run_command(command, CONFIG)).strip()
    if response.strip().startswith("Saving map"):
        return ASGIRedirectResponse(
            "/?saved=true&filename={}".format((data.filename or "").strip())
        )
    raise HTTPException(status_code=500, detail="Error saving game.")


@post("/rcon", media_type=MediaType.JSON)
async def rcon_command(data: RconCommand) -> dict[str, str]:
    """Execute arbitrary RCON command and return raw response"""
    response = await run_command([data.command], CONFIG)
    return {"result": response}


def app_exception_handler(
    request: Request[Any, Any, Any], exc: HTTPException
) -> Response[Any]:
    if exc.status_code < 500:
        return Response(
            content={
                "error": f"client error {exc.status_code}",
                "path": request.url.path,
                "status_code": exc.status_code,
            },
            status_code=exc.status_code,
        )
    return Response(
        content={
            "error": "server error",
            "path": request.url.path,
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
        status_code=500,
    )


def router_handler_exception_handler(
    request: Request[Any, Any, Any], exc: ValidationException
) -> Response[Any]:
    return Response(
        content={"error": "validation error", "path": request.url.path},
        status_code=400,
    )


logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["queue_listener"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    log_exceptions="always",
)

app = Litestar(
    logging_config=logging_config,
    exception_handlers={HTTPException: app_exception_handler},
    route_handlers=[
        index_html,
        list_players,
        list_admins,
        get_seed,
        get_uptime,
        save_game,
        shutdown_server,
        rcon_command,
        static_file,
    ],
    middleware=[HostLimiterMiddleware(allow_list=ALLOWLIST)],
)

__all__ = ["app"]
