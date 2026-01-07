from typing import List, Optional

from ninegag_notion_scraper.domain.interfaces.repositories.cookie \
    import CookieRepo


class CookiesUseCase:
    def __init__(self,
                 cookie_repo: CookieRepo
                 ) -> None:
        self.cookie_repo = cookie_repo

    def get_cookies(self, ignore_errors: bool = True) -> Optional[List[dict]]:
        """
        Returns the cookies stored in the repository.

        :param ignore_errors: Whether to ignore errors when retrieving
            cookies
        :type ignore_errors: bool
        :return: The list of cookies or None if an error occurs and
            ignore_errors is True
        :rtype: List[dict[Any, Any]] | None
        """
        try:
            return self.cookie_repo.get_cookies()
        except Exception as e:
            if ignore_errors:
                return None
            raise e

    def save_cookies(self, data: List[dict]) -> None:
        self.cookie_repo.save_cookies(data)
