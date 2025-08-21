from typing import Protocol, List, Optional

from ninegag_notion_scraper.app.entities.meme import PostMeme, DBMeme


class GetPostMemesRepo(Protocol):
    at_end: bool

    def get_memes(self) -> List[PostMeme]:
        ...

    def next(self) -> int:
        ...


class GetDBMemesRepo(Protocol):
    at_end: bool

    def get_memes(self, filter: Optional[dict]) -> List[DBMeme]:
        ...

    def next(self) -> int:
        ...


class SaveMemeRepo(Protocol):
    def save_meme(self,
                  meme: PostMeme,
                  update: bool = False
                  ) -> None:
        ...

    def meme_exists(self, meme: PostMeme | DBMeme) -> bool:
        ...


class GetMemeRepo(Protocol):
    def get_meme_from_url(self, url: str) -> PostMeme:
        ...


class UpdateMemeRepo(Protocol):
    def update_meme(self, id: str, tags: list) -> None:
        ...

    def meme_exists(self, meme: PostMeme | DBMeme) -> bool:
        ...
