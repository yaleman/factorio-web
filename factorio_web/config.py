import ipaddress
from typing import List, Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    rcon_host: str = Field("localhost", description="RCON server host")
    rcon_port: int = Field(27015, description="RCON server port")
    rcon_password: SecretStr = Field(SecretStr(""), description="RCON server password")
    rcon_allowlist: Optional[str] = Field(
        None, description="Comma-separated list of allowed IP addresses or networks"
    )

    model_config = SettingsConfigDict(env_prefix="")

    def allowlist(self) -> List[ipaddress.IPv4Network | ipaddress.IPv6Network]:
        if not self.rcon_allowlist:
            return []
        networks: List[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
        for part in self.rcon_allowlist.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                network = ipaddress.ip_network(part, strict=False)
                networks.append(network)
            except ValueError:
                try:
                    network = ipaddress.ip_network(f"{part}/32", strict=False)
                    networks.append(network)
                    continue
                except ValueError:
                    print("Invalid allowlist entry:", part)

                print("Invalid allowlist entry:", part)
                pass  # Ignore invalid entries
        return networks
