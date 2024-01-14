import logging
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


from ninegag_notion_scraper.app.entities.meme import Meme
from ninegag_notion_scraper.app.interfaces.repositories.meme \
    import GetMemeRepo
from ninegag_notion_scraper.app.use_cases.cookies import CookiesUseCase

from .element_article import SinglePageArticle
from .base import BaseScraperRepo, ScraperNotSetup


logger = logging.getLogger('app.9gag')


class Meme404(Exception):
    pass


class NineGagSinglePageScraperRepo(BaseScraperRepo, GetMemeRepo):
    def __init__(self, username: str, password: str,
                 web_driver: WebDriver, cookie_usecase: CookiesUseCase,
                 **kwargs) -> None:
        BaseScraperRepo.__init__(self, username, password, web_driver,
                                 cookie_usecase, **kwargs)

    def get_meme_from_url(self, url: str) -> Meme:
        if not self._is_setup:
            raise ScraperNotSetup

        self.web_driver.get(url)

        try:
            section_element = self.web_driver.find_element(
                By.CSS_SELECTOR, "#individual-post"
            )
        except NoSuchElementException:
            logger.error("Unable to find section element on page")
            self._is_404_page()
            raise

        try:
            article = section_element.find_element(By.CSS_SELECTOR, "article")
        except NoSuchElementException:
            logger.error("Unable to find article element on page")
            raise

        return Meme(
            title=SinglePageArticle.get_title_from_article(article),
            item_id=SinglePageArticle.get_item_id_from_url(url),
            post_web_url=url,
            tags=SinglePageArticle.get_tags_from_article(article),
            cover_photo_url=SinglePageArticle.get_cover_photo_from_article(
                article),
            post_file_url=SinglePageArticle.get_file_url_from_article(article)
        )

    def _is_404_page(self):
        logger.debug("Checking if its 404 page")
        try:
            message404_element = self.web_driver.find_element(
                By.CSS_SELECTOR, "div.message > h1"
            )
            message404 = message404_element.get_attribute('innerHTML')
            pass
            if "404" == message404:
                raise Meme404
        except NoSuchElementException:
            raise
