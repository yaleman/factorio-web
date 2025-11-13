import os
from pathlib import Path
from typing import Annotated, List
import re
from litestar import Litestar, get, MediaType, post, Response
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.exceptions import HTTPException

from .models import PlayerInfo, PlayersInfo, UptimeResponse, SaveForm, RconCommand
from .rcon_command import run_command
from .config import Settings

MY_PATH = os.path.dirname(__file__)
CONFIG = Settings.model_validate({})


@get("/", media_type=MediaType.HTML)
async def index_html() -> str:
    with open(os.path.join(MY_PATH, "static", "index.html"), "r") as f:
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
) -> str:
    command = ["/save"]
    if data is not None and data.filename is not None and data.filename.strip() != "":
        command.append(data.filename)
    response = (await run_command(command, CONFIG)).strip()
    if response.strip().startswith("Saving map"):
        filename = response.strip().split()[-1]
        return f'"{filename}"'
    raise HTTPException(status_code=500, detail="Error saving game.")


@post("/rcon", media_type=MediaType.JSON)
async def rcon_command(data: RconCommand) -> dict[str, str]:
    """Execute arbitrary RCON command and return raw response"""
    response = await run_command([data.command], CONFIG)
    return {"result": response}


app = Litestar(
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
)

__all__ = ["app"]
