[private]
default:
    just --list


reload:
    uv run uvicorn 'factorio_web:app' --reload --port 8001 --host 0.0.0.0


check: lint mypy test

lint:
    uv run ruff check factorio_web tests

mypy:
    uv run mypy --strict factorio_web tests

test:
    uv run pytest