from litestar.exceptions import HTTPException
from rcon.source import rcon  # type: ignore[import-untyped]
from rcon.exceptions import WrongPassword  # type: ignore[import-untyped]

from factorio_web.config import Settings


async def run_command(command: list[str], config: Settings) -> str:
    try:
        res: str = await rcon(
            *command,
            host=config.rcon_host,
            port=config.rcon_port,
            passwd=config.rcon_password,
        )
        return res
    except WrongPassword:
        print("RCON error: Wrong password")
        raise HTTPException(status_code=500, detail="Wrong password for RCON.")
    except Exception as e:
        print(f"RCON error: {e=}")
        raise HTTPException(status_code=500, detail="RCON command failed.")
