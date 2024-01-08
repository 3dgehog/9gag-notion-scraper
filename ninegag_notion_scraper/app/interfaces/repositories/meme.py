from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

from ninegag_notion_scraper.app.entities.meme import Meme


@dataclass
class GetMemesRepo(ABC):
    at_end: bool

    @abstractmethod
    def get_memes(self) -> List[Meme]:
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


class SaveMemeRepo(ABC):
    @abstractmethod
    def save_meme(self,
                  meme: Meme,
                  update: bool = False
                  ) -> None:
        ...

    @abstractmethod
    def meme_exists(self, meme: Meme) -> bool:
        ...
