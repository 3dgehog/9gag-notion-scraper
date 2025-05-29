import os
from pydantic import BaseModel, Field


class Environments(BaseModel):
    NOTION_TOKEN: str
    NOTION_DATABASE: str
    NINEGAG_USERNAME: str = Field(alias="USERNAME")
    NINEGAG_PASSWORD: str = Field(alias="PASSWORD")
    NINEGAG_URL: str = Field(alias="9GAG_URL")
    PERSONAL_URL: str = Field(default="172.30.0.10:5000/WebDAV/9gag-memes")
    COVERS_PATH: str = Field(default="./dump/covers")
    MEMES_PATH: str = Field(default="./dump/memes")

    @classmethod
    def from_env(cls):
        values = {}
        for name, field in cls.model_fields.items():
            env_name = field.alias or name
            if field.default is not None:
                values[name] = os.getenv(env_name, field.default)
            else:
                values[name] = os.environ[env_name]
        return cls(**values)


def get_envs() -> Environments:
    return Environments.from_env()
