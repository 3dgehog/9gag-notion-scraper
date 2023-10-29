from abc import ABC, abstractmethod

from ninegag_notion_scraper.scrapers.entities import Meme


class AbstractStorageRepo(ABC):

    @abstractmethod
    def save_meme(self, meme: Meme, update: bool = False) -> None:
        raise NotImplementedError
