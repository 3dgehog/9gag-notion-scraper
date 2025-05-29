from pydantic import Field
from pydantic_settings import BaseSettings


class Environments(BaseSettings):
    NOTION_TOKEN: str = Field(default="", min_length=1)
    NOTION_DATABASE: str = Field(default="", min_length=1)
    NINEGAG_USERNAME: str = Field(default="", alias="USERNAME", min_length=1)
    NINEGAG_PASSWORD: str = Field(default="", alias="PASSWORD", min_length=1)
    NINEGAG_URL: str = Field(default="", alias="9GAG_URL", min_length=1)
    PERSONAL_URL: str = Field(default="172.30.0.10:5000/WebDAV/9gag-memes")
    COVERS_PATH: str = Field(default="./dump/covers")
    MEMES_PATH: str = Field(default="./dump/memes")
    RUN_INTERVAL_SECONDS: str = Field(default="0")
    WEBDRIVER_URL: str = Field(default="0")
    LOG_LEVEL: str = Field(
        default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")


def get_envs():
    return Environments()
