"""9GAG"""
import time
import os
import logging
import pickle
from dataclasses import dataclass
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

chrome_options = webdriver.ChromeOptions()

# Disable images loaded
# image_prefs = {"profile.managed_default_content_settings.images": 2}
# chrome_options.add_experimental_option("prefs", image_prefs)

logger = logging.getLogger('app.9gag')

# temp_driver = webdriver.Chrome()
# print(temp_driver.capabilities['chrome']['chromedriverVersion'])
# exit

# Headless
if os.environ.get('HEADLESS'):
    chrome_options.add_argument('headless')
    chrome_options.add_argument("user-agent=Chrome/96.0.4664.110")

LOGIN_URL = 'https://9gag.com/login'

DEFAULT_IMPLICITY_WAIT = 1

PICKLE_COOKIES = "cookies.pkl"

WEB_DRIVER = webdriver.Chrome(options=chrome_options)


@dataclass
class ArticleData:
    name: str
    id: str
    url: str
    post_section: list
    cover_photo: str

    def __post_init__(self):
        logger.debug("Created %s", self)


class NineGagTools:
    """A class that handles all the web scraping on 9gag"""

    def __init__(self, url: str, username: str, password: str) -> None:
        self.url = url
        self.username = username
        self.password = password
        self.web_driver = WEB_DRIVER
        self.at_bottom_flag = False

        self._login_flag = False
        self._attempted_login_flag = False
        self._list_view: WebElement
        self._current_stream_num = 0

        self.web_driver.implicitly_wait(DEFAULT_IMPLICITY_WAIT)

        self._setup(url)

    def _setup(self, url: str):
        self._load_cookies()
        self.web_driver.get(url)

        if not self._login_flag:
            if not self._is_logged_in():
                self._login()

        self._list_view = self._get_list_view()

    def _load_cookies(self):
        if os.path.exists(PICKLE_COOKIES):
            with open(PICKLE_COOKIES, "rb") as pcookie:
                cookies = pickle.load(pcookie)
            for cookie in cookies:
                self.web_driver.add_cookie(cookie)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.web_driver.quit()

    def _is_logged_in(self):
        title = self.web_driver.find_element(
            By.XPATH, '/html/head/title').get_attribute('innerHTML')
        if title == "9GAG - 404 Nothing here":
            self._login_flag = False
            logger.debug("Detected you are NOT logged in")
            if self._attempted_login_flag:
                raise RuntimeError("Wasn't able to login... Help")
            return False

        self._login_flag = True
        logger.debug("Detected you are logged in")
        return True

    def _login(self):
        logger.debug("Attempting to login")
        self.web_driver.get(LOGIN_URL)

        time.sleep(1)

        username_field = self.web_driver.find_element(
            By.CSS_SELECTOR,
            '#signup > form > div > div:nth-child(3) > input[type=text]'
        )
        password_field = self.web_driver.find_element(
            By.CSS_SELECTOR,
            '#signup > form > div > div:nth-child(4) > input[type=password]'
        )

        username_field.clear()
        password_field.clear()
        username_field.send_keys(self.username)
        password_field.send_keys(self.password)

        login_button = self.web_driver.find_element(
            By.CSS_SELECTOR,
            '#signup > form > div > button.ui-btn.btn-color-primary.login-view__login'  # noqa
        )

        login_button.click()

        time.sleep(1)

        self._attempted_login_flag = True

        self._is_logged_in()

        pickle.dump(self.web_driver.get_cookies(), open(PICKLE_COOKIES, "wb"))

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

    def get_memes(self) -> List[ArticleData]:
        """Return memes from current stream"""
        if self.at_bottom_flag:
            logger.warning("Reached the bottom, no more memes to give")
            return []

        stream = self._get_stream(self._current_stream_num)
        articles = self._get_article_from_stream(stream)

        elements = []

        for article in articles:
            try:
                tags = self._get_tags_from_article(article)

                if 'Promoted' in tags:
                    logger.debug("Skipping Promoted Post")
                    continue

                url = self._get_url_from_article(article)

                articledata = ArticleData(
                    name=self._get_title_from_article(article),
                    id=os.path.basename(url),
                    url=url,
                    post_section=tags,
                    cover_photo=self._get_cover_photo_from_article(article)
                )
            except NoSuchElementException:
                logger.warning("Skipping Article because of missing element")
                continue

            elements.append(articledata)

        return elements

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

    def _get_article_from_stream(self, stream: WebElement) -> List[WebElement]:
        try:
            articles = stream.find_elements(By.TAG_NAME, 'article')
        except NoSuchElementException as error:
            logger.warning('Unable to find articles in stream %s',
                           stream.get_attribute('outerHTML')
                           )
            raise error
        return articles

    def _get_tags_from_article(self, article: WebElement) -> List[str | None]:
        try:
            tags_element = article.find_elements(
                By.CSS_SELECTOR,
                'article > div.post-tag.listview > a'
            )
            tags = [
                x.get_attribute('innerHTML')
                for x in tags_element
            ]
        except NoSuchElementException as error:
            logger.warning('Unable to find post_section in article %s',
                           article.get_attribute('outerHTML')
                           )
            raise error

        return tags

    def _get_cover_photo_from_article(self, article: WebElement) -> str:
        self.web_driver.implicitly_wait(0)
        cover_photo = None

        try:
            cover_photo = article.find_element(
                By.CSS_SELECTOR, '.post-container * > picture > img'
            ).get_attribute('src')
        except NoSuchElementException:
            pass

        try:
            cover_photo = article.find_element(
                By.CSS_SELECTOR, '.post-container * > video'
            ).get_attribute('poster')
        except NoSuchElementException:
            pass

        self.web_driver.implicitly_wait(DEFAULT_IMPLICITY_WAIT)

        if not cover_photo:
            logger.warning("Unable to find cover photo\n %s",
                           article.get_attribute('outerHTML')
                           )
            raise NoSuchElementException("Unable to find cover photo")

        return cover_photo

    def _get_title_from_article(self, article: WebElement) -> str:
        try:
            title = article.find_element(
                By.CSS_SELECTOR,
                'article > header > a').text
        except NoSuchElementException as error:
            logger.warning('Unable to find title in article %s',
                           article.get_attribute('outerHTML')
                           )
            raise error

        return title

    def _get_url_from_article(self, article: WebElement) -> str:
        try:
            url = article.find_element(
                By.CSS_SELECTOR,
                'article > header > a').get_attribute('href')
        except NoSuchElementException as error:
            logger.warning('Unable to find title in article %s',
                           article.get_attribute('outerHTML')
                           )
            raise error

        assert url
        return url

    def next_page(self, **kwargs) -> int:
        """Goes to the next stream"""
        if self.at_bottom_flag:
            logger.warning("Reached the bottom, no more pages")
            return self._current_stream_num

        self._current_stream_num += 1
        self._scroll_to_spinner(**kwargs)

        if not self._is_loader_spinning():
            self.at_bottom_flag = True

        return self._current_stream_num

    def _does_stream_num_exists(self, stream_num: int) -> bool:
        try:
            self._get_stream(stream_num)
        except NoSuchElementException:
            logger.info("End of the page reached")
            return False
        return True

    def _scroll_by(self, sleep=0.5, scroll=500):
        self.web_driver.execute_script(f"window.scrollBy(0,{scroll})", "")
        time.sleep(sleep)

    def _scroll_to_spinner(self, sleep: int = 1):
        element = self._get_loader_element()
        actions = ActionChains(self.web_driver)
        actions.move_to_element(element).perform()
        time.sleep(sleep)

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

        loader = self._get_loader_element().get_attribute('class')

        if "spin" in loader:
            return True
        elif "end" in loader:
            return False
        else:
            logger.warning('Unable to detect loader status %s',
                           loader.get_attribute('outerHTML')
                           )
            raise RuntimeError('Cannot detect loader')
