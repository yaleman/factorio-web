from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    rcon_host: str
    rcon_port: int
    rcon_password: str

    model_config = SettingsConfigDict(env_prefix="")
