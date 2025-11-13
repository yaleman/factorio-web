from typing import Optional
from pydantic import BaseModel, Field


class PlayerInfo(BaseModel):
    name: str
    online: bool


class PlayersInfo(BaseModel):
    count: int
    players: dict[str, PlayerInfo]


class UptimeResponse(BaseModel):
    minutes: Optional[int] = Field(None)
    hours: Optional[int] = Field(None)
    seconds: Optional[int] = Field(None)


class SaveForm(BaseModel):
    filename: Optional[str] = None


class RconCommand(BaseModel):
    command: str
