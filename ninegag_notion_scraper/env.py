import os
from pydantic import BaseModel


class Environments(BaseModel):
    NOTION_TOKEN: str
    NOTION_DATABASE: str
    NINEGAG_USERNAME: str
    NINEGAG_PASSWORD: str
    NINEGAG_URL: str
    PERSONAL_URL: str
    COVERS_PATH: str
    MEMES_PATH: str


def get_envs() -> Environments:
    return Environments(
        NOTION_TOKEN=os.environ["NOTION_TOKEN"],
        NOTION_DATABASE=os.environ["NOTION_DATABASE"],
        NINEGAG_USERNAME=os.environ['USERNAME'],
        NINEGAG_PASSWORD=os.environ['PASSWORD'],
        NINEGAG_URL=os.environ['9GAG_URL'],
        PERSONAL_URL="172.30.0.10:5000/WebDAV/9gag-memes",
        COVERS_PATH=os.getenv("COVERS_PATH", "./dump/covers"),
        MEMES_PATH=os.getenv("MEMES_PATH", "./dump/memes")
    )
