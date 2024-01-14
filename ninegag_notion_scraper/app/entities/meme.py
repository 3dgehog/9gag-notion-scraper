from typing import Optional
from pydantic import BaseModel


class Meme(BaseModel):
    title: str
    item_id: str
    post_web_url: str
    tags: list
    cover_photo_url: str
    post_file_url: Optional[str]
