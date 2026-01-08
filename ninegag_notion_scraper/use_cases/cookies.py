from typing import List, Optional

from ninegag_notion_scraper.domain.interfaces.repositories.cookie \
    import CookieRepo


def get_cookies(cookie_repo: CookieRepo,
                ignore_errors: bool = True) -> Optional[List[dict]]:
    """
    Returns the cookies stored in the repository.

    :param cookie_repo: The cookie repository to get cookies from
    :type cookie_repo: CookieRepo
    :param ignore_errors: Whether to ignore errors when retrieving
        cookies
    :type ignore_errors: bool
    :return: The list of cookies or None if an error occurs and
        ignore_errors is True
    :rtype: List[dict[Any, Any]] | None
    """
    try:
        return cookie_repo.get_cookies()
    except Exception as e:
        if ignore_errors:
            return None
        raise e


def save_cookies(cookie_repo: CookieRepo, data: List[dict]) -> None:
    """
    Saves the cookies to the repository.

    :param cookie_repo: The cookie repository to save cookies to
    :type cookie_repo: CookieRepo
    :param data: The list of cookies to save
    :type data: List[dict]
    """
    cookie_repo.save_cookies(data)
