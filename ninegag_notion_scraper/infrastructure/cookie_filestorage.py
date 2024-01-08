import os
import pickle
from typing import List, Optional
from ninegag_notion_scraper.app.interfaces.repositories.cookie \
    import CookieRepo

PICKLE_COOKIES = "cookies.pkl"


class FileCookiesRepo(CookieRepo):
    def get_cookies(self) -> Optional[List[dict]]:
        if not os.path.exists(PICKLE_COOKIES):
            return None

        with open(PICKLE_COOKIES, "rb") as pcookie:
            cookies = pickle.load(pcookie)
        return cookies

    def save_cookies(self, data: List[dict]) -> None:
        pickle.dump(data, open(PICKLE_COOKIES, "wb"))
