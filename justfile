[private]
default:
    just --list


reload:
    uv run granian --interface asgi 'factorio_web:app' --reload --port 8001 --host 0.0.0.0

check: lint mypy test

lint:
    uv run ruff check factorio_web tests

mypy:
    uv run mypy --strict factorio_web tests

test:
    uv run pytest

docker_run:
    docker build -t factorio-web .
    docker run -p 8001:8001 \
        -e RCON_HOST=${RCON_HOST} \
        -e RCON_PORT=${RCON_PORT} \
        -e RCON_PASSWORD=${RCON_PASSWORD} \
        -e RCON_ALLOWLIST=${RCON_ALLOWLIST} \
     factorio-web