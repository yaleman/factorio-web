"""things"""

import uvicorn

from factorio_web import app, CONFIG


def main() -> None:
    if CONFIG.rcon_password.get_secret_value().strip() == "":
        print(
            "RCON password is not set. This is likely to cause problems! Set the RCON_PASSWORD environment variable."
        )
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
