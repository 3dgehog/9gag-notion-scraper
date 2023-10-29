from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from ..entities import Meme


@dataclass
class AbstractScraperRepo(ABC):
    at_bottom: bool

    @abstractmethod
    def get_memes(self) -> List[Meme]:
        raise NotImplementedError

    @abstractmethod
    def next_page(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exception_type, exception_value, traceback):
        raise NotImplementedError
