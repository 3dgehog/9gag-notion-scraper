from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

from ninegag_notion_scraper.app.entities.meme import PostMeme, DBMeme


@dataclass
class GetPostMemesRepo(ABC):
    at_end: bool

    @abstractmethod
    def get_memes(self) -> List[PostMeme]:
        raise NotImplementedError

    @abstractmethod
    def next(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exception_type, exception_value, traceback):
        raise NotImplementedError


@dataclass
class GetDBMemesRepo(ABC):
    at_end: bool

    @abstractmethod
    def get_memes(self, filter: Optional[dict]) -> List[DBMeme]:
        raise NotImplementedError

    @abstractmethod
    def next(self) -> int:
        raise NotImplementedError


class SaveMemeRepo(ABC):
    @abstractmethod
    def save_meme(self,
                  meme: PostMeme,
                  update: bool = False
                  ) -> None:
        ...

    @abstractmethod
    def meme_exists(self, meme: PostMeme | DBMeme) -> bool:
        ...


class GetMemeRepo(ABC):

    @abstractmethod
    def get_meme_from_url(self, url: str) -> PostMeme:
        ...


class UpdateMemeRepo(ABC):
    @abstractmethod
    def update_meme(self, id: str, tags: list) -> None:
        ...

    @abstractmethod
    def meme_exists(self, meme: PostMeme | DBMeme) -> bool:
        ...
