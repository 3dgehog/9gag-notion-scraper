from abc import ABC, abstractmethod
from typing import List, Optional


class GetCookiesRepo(ABC):
    @abstractmethod
    def get_cookies(self) -> Optional[List[dict]]:
        raise NotImplementedError


class SaveCookiesRepo(ABC):
    @abstractmethod
    def save_cookies(self, data: List[dict]) -> None:
        raise NotImplementedError


class CookieRepo(GetCookiesRepo, SaveCookiesRepo):
    pass
