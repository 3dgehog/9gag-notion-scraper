from typing import List, Optional, Protocol


class CookieRepo(Protocol):
    def get_cookies(self) -> Optional[List[dict]]:
        ...

    def save_cookies(self, data: List[dict]) -> None:
        ...
