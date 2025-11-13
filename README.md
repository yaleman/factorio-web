# Factorio Web RCON Interface

A web interface for managing Factorio game servers via RCON protocol.

## Quick Start

```bash
# Set environment variables
export RCON_HOST=localhost
export RCON_PORT=27015
export RCON_PASSWORD=your_password

# Run development server
just reload

# Or run production server
uv run factorio-web
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RCON_HOST` | `localhost` | Factorio server hostname |
| `RCON_PORT` | `27015` | RCON port |
| `RCON_PASSWORD` | _(empty)_ | RCON password |

## Features

- **Live Player List** - Auto-refreshing list of online/offline players
- **Admin Management** - View server admins and their status
- **Server Info** - Display world seed and game uptime
- **Save Game** - Trigger manual saves with optional filename
- **RESTful API** - JSON endpoints for programmatic access

## API Endpoints

- `GET /players` - Player list with status
- `GET /admins` - Admin list with status
- `GET /seed` - World seed
- `GET /uptime` - Game time (hours/minutes/seconds)
- `POST /save` - Save game (optional filename)
- `POST /shutdown` - Stop server

## Development

```bash
# Type checking
mypy --strict factorio_web/

# Linting
ruff check factorio_web/

# Formatting
ruff fmt factorio_web/
```
