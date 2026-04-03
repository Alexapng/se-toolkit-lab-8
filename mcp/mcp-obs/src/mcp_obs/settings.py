"""Settings for mcp-obs MCP server."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Read VictoriaLogs/Traces URLs from environment."""

    nanobot_victorialogs_url: str = Field(
        default="http://victorialogs:9428",
        alias="NANOBOT_VICTORIALOGS_URL",
    )
    nanobot_victoriatraces_url: str = Field(
        default="http://victoriatraces:10428",
        alias="NANOBOT_VICTORIATRACES_URL",
    )


settings = Settings.model_validate({})
