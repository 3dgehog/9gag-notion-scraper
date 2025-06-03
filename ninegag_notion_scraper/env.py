from pydantic import Field
from pydantic_settings import BaseSettings


import re
from pydantic import field_validator


class Environments(BaseSettings):
    NOTION_TOKEN: str = Field(default="", min_length=1)
    NOTION_DATABASE: str = Field(default="", min_length=1)
    NINEGAG_USERNAME: str = Field(default="", alias="USERNAME", min_length=1)
    NINEGAG_PASSWORD: str = Field(default="", alias="PASSWORD", min_length=1)
    NINEGAG_URL: str = Field(default="", alias="9GAG_URL", min_length=1)
    PERSONAL_URL: str = Field(default="172.30.0.10:5000/WebDAV/9gag-memes")
    COVERS_PATH: str = Field(default="./covers")
    MEMES_PATH: str = Field(default="./memes")
    RUN_INTERVAL_SECONDS: str = Field(default="0")
    WEBDRIVER_URL: str = Field(default="")
    LOG_LEVEL: str = Field(default="INFO")
    BROWSER: str = Field(default="firefox")

    @field_validator("WEBDRIVER_URL")
    def validate_webdriver_url(cls, v):
        pattern = r"(^$|^https?://.+)"
        if not re.match(pattern, v):
            raise ValueError("The WEBDRIVER_URL url pattern is not correct")
        return v

    @field_validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v

    @field_validator("BROWSER")
    def validate_browser(cls, v):
        allowed = {"firefox", "chrome"}
        if v not in allowed:
            raise ValueError(f"BROWSER must be one of {allowed}")
        return v


def get_envs():
    return Environments()
