[private]
default:
    just --list


reload:
    uv run uvicorn 'factorio_web:app' --reload --port 8001 --host '127.0.0.1'