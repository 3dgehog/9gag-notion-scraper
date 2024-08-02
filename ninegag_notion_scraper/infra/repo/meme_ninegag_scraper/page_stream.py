import time
import logging
from typing import List
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

from ninegag_notion_scraper.app.entities.meme import PostMeme
from ninegag_notion_scraper.app.interfaces.meme_repo \
    import GetPostMemesRepo
from ninegag_notion_scraper.app.use_cases.cookies import CookiesUseCase

from .base import BaseScraperRepo, ScraperNotSetup
from .element_article import StreamArticle

logger = logging.getLogger('app.9gag')


class NineGagStreamScraperRepo(BaseScraperRepo, GetPostMemesRepo):
    """A class that handles all the web scraping on 9gag"""

    def __init__(self,
                 url: str,
                 username: str,
                 password: str,
                 web_driver: WebDriver,
                 cookie_usecase: CookiesUseCase,
                 **kwargs) -> None:

        BaseScraperRepo.__init__(self, username, password,
                                 web_driver, cookie_usecase,
                                 **kwargs)

        self._stream_url = url
        self._at_bottom_flag = self.at_end
        self._list_view: WebElement
        self._current_stream_num = 0

    def get_memes(self) -> List[PostMeme]:
        """Return memes from current stream"""
        if not self._is_setup:
            raise ScraperNotSetup
        if self._at_bottom_flag:
            logger.warning("Reached the bottom, no more memes to give")
            return []

        stream = self._get_stream(self._current_stream_num)
        articles = self._get_articles_from_stream(stream)

        elements = []

        for article in articles:
            try:
                tags = StreamArticle.get_tags_from_article(article)

                if 'Promoted' in tags:
                    logger.debug("Skipping Promoted Post")
                    continue

                url = StreamArticle.get_url_from_article(article)

                articledata = PostMeme(
                    post_title=StreamArticle.get_title_from_article(article),
                    post_id=StreamArticle.get_item_id_from_url(url),
                    post_url=url,
                    post_tags=StreamArticle.get_tags_from_article(article),
                    post_cover_photo_url=StreamArticle.
                    get_cover_photo_from_article(article),
                    post_file_url=StreamArticle.get_file_url_from_article(
                        article)
                )
            except NoSuchElementException:
                logger.warning("Skipping Article because of missing element")
                continue

            elements.append(articledata)

        return elements

    def next(self) -> int:
        """Goes to the next stream"""
        if self._at_bottom_flag:
            logger.warning("Reached the bottom, no more pages")
            return self._current_stream_num

        self._current_stream_num += 1
        self._scroll_to_spinner()

        if not self._is_loader_spinning():
            self._at_bottom_flag = True

        return self._current_stream_num

    def _setup(self) -> None:
        super()._setup()
        self.web_driver.get(self._stream_url)
        self._list_view = self._get_list_view()

    def _get_articles_from_stream(self,
                                  stream: WebElement
                                  ) -> List[WebElement]:
        try:
            articles = stream.find_elements(By.TAG_NAME, 'article')
        except NoSuchElementException as error:
            logger.warning('Unable to find articles in stream %s',
                           stream.get_attribute('outerHTML')
                           )
            raise error
        return articles

    def _get_list_view(self) -> WebElement:
        try:
            list_view = self.web_driver.find_element(
                By.CSS_SELECTOR,
                '#list-view-2'
            )
        except NoSuchElementException as error:
            logger.warning("Unable to find list_view on page\n %s",
                           self.web_driver.page_source)
            raise error

        return list_view

    def _get_stream(self, stream_num: int) -> WebElement:
        try:
            stream: WebElement = self._list_view.find_element(
                By.CSS_SELECTOR,
                f'#stream-{stream_num}')
        except NoSuchElementException as error:
            logger.warning(f"Unable to find stream {stream_num}" +
                           f"{self._list_view.get_attribute('outerHTML')}"
                           )
            raise error

        return stream

    def _does_stream_num_exists(self, stream_num: int) -> bool:
        try:
            self._get_stream(stream_num)
        except NoSuchElementException:
            logger.info("End of the page reached")
            return False
        return True

    def _scroll_by(self, scroll=500):
        self.web_driver.execute_script(f"window.scrollBy(0,{scroll})", "")
        time.sleep(self.sleep)

    def _scroll_to_spinner(self):
        element = self._get_loader_element()
        actions = ActionChains(self.web_driver)
        actions.scroll_to_element(element).perform()
        time.sleep(self.sleep)

    def _get_loader_element(self) -> WebElement:
        try:
            loader = self._list_view.find_element(
                By.CSS_SELECTOR, 'div.loading > a'
            )
        except NoSuchElementException as error:
            logger.warning('Unable to find loader in list_view %s',
                           self._list_view.get_attribute('outerHTML')
                           )
            raise error
        return loader

    def _is_loader_spinning(self):
        """9Gag has an element at the bottom of the list that has either a
        spin or end state. this state can be used to determine if you are
        at the end of the list of memes on the page. If there are still
        memes to load, it will be spinning"""

        loader = self._get_loader_element()
        loader_class = loader.get_attribute('class')

        assert loader_class

        if "spin" in loader_class.split(" "):
            return True
        elif "end" in loader_class.split(" "):
            return False
        else:
            logger.warning('Unable to detect loader status %s',
                           loader.get_attribute('outerHTML')
                           )
            raise RuntimeError('Cannot detect loader')
