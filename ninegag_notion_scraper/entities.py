from dataclasses import dataclass


@dataclass
class Meme:
    title: str
    item_id: str
    post_web_url: str
    tags: list
    cover_photo_url: str
    post_file_url: str
