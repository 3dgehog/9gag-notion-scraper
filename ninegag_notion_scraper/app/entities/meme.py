from typing import Optional
from pydantic import BaseModel


class BaseMeme(BaseModel):
    post_title: str
    post_id: str
    post_url: str
    post_tags: list
    post_cover_photo_url: str


class PostMeme(BaseMeme):
    post_file_url: str


class DBMeme(BaseMeme):
    note: Optional[str]
    tags: list
