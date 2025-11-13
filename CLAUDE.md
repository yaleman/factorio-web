# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web API that provides HTTP access to a Factorio game server via RCON (Remote Console). Built with Litestar framework, it exposes endpoints for querying server status, managing players, and executing server commands.

## Development Commands

### Running the Application
```bash
# Development server with auto-reload
just reload

# Production server
uv run factorio-web
```

### Type Checking
```bash
mypy --strict factorio_web/
```

### Linting
```bash
ruff check factorio_web/
```

### Formatting
```bash
ruff fmt factorio_web/
```

### Testing
```bash
pytest
```

Note: Currently no tests exist in the codebase.

## Architecture

### Core Components

- **factorio_web/__init__.py** - Main Litestar application with all HTTP route handlers
- **factorio_web/rcon.py** - RCON client wrapper that handles communication with Factorio server
- **factorio_web/models.py** - Pydantic models for API request/response validation
- **factorio_web/__main__.py** - Application entry point

### RCON Communication Pattern

All endpoints follow the same pattern:
1. Call `run_command()` with a list of RCON command arguments
2. Parse the text response from Factorio server
3. Return structured JSON data (except root endpoint which returns HTML)

The `run_command()` function handles RCON connection, authentication, and error handling centrally. RCON credentials are configured via environment variables:
- `RCON_HOST` (default: localhost)
- `RCON_PORT` (default: 27015)
- `RCON_PASSWORD` (default: empty string)

### Response Parsing

Most endpoints parse text-based RCON responses using string manipulation:
- `/players` - Parses player list with online status
- `/admins` - Similar parsing to players
- `/uptime` - Uses regex to extract hours/minutes/seconds
- `/seed` - Simple integer conversion
- `/save` - Extracts filename from response

## Dependencies

- **litestar** - Web framework
- **pydantic** - Data validation via models
- **rcon** - RCON protocol client for Factorio server communication
- **uvicorn** - ASGI server

## Development Notes

- Python 3.12+ required
- Uses `uv` for package management
- No test suite currently exists
- RCON commands are Factorio-specific (e.g., `/players`, `/seed`, `/time`)
- Error handling converts RCON exceptions to HTTP 500 errors
