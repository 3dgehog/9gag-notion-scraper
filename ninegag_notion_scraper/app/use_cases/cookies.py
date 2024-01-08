from typing import List, Optional

from ninegag_notion_scraper.app.interfaces.repositories.cookie \
    import CookieRepo


class CookiesUseCase:
    def __init__(self,
                 cookie_repo: CookieRepo
                 ) -> None:
        self.cookie_repo = cookie_repo

    def get_cookies(self) -> Optional[List[dict]]:
        return self.cookie_repo.get_cookies()

    def save_cookies(self, data: List[dict]) -> None:
        self.cookie_repo.save_cookies(data)
