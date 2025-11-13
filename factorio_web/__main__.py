"""things"""

import uvicorn

from factorio_web import app


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
