import os
from typing import Any

from litestar.exceptions import HTTPException
from rcon.source import rcon
from rcon.exceptions import WrongPassword


async def run_command(command: list[str]) -> Any:
    try:
        return await rcon(
            *command,
            host=os.getenv("RCON_HOST") or "localhost",
            port=int(os.getenv("RCON_PORT", "27015")),
            passwd=os.getenv("RCON_PASSWORD", ""),
        )
    except WrongPassword:
        print("RCON error: Wrong password")
        raise HTTPException(status_code=500, detail="Wrong password for RCON.")
    except Exception as e:
        print(f"RCON error: {e=}")
        raise HTTPException(status_code=500, detail="RCON command failed.")
