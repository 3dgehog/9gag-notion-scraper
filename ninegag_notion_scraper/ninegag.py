import time
import os
import logging
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

chrome_options = webdriver.ChromeOptions()

# Disable images loaded
# image_prefs = {"profile.managed_default_content_settings.images": 2}
# chrome_options.add_experimental_option("prefs", image_prefs)

# Headless
# chrome_options.add_argument('headless')

logger = logging.getLogger('app.9gag')

NINEGAG_URL = os.environ['9GAG_URL']
LOGIN_URL = 'https://9gag.com/login'

USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']

DEFAULT_IMPLICITY_WAIT = 1


class NineGagBot(webdriver.Chrome):
    def __init__(self, url=NINEGAG_URL):
        self.url = url
        self._current_stream = 0
        self.at_bottom_flag = False
        self.login_flag = False
        self.attempted_login_flag = False
        super().__init__(chrome_options=chrome_options)
        self.implicitly_wait(DEFAULT_IMPLICITY_WAIT)
        self._list_view_element = None

    def __exit__(self, *args) -> None:
        self.quit()
        logger.debug("Exiting Browser")
        return super().__exit__(*args)

    def landing_page(self):
        self.get(self.url)
        if not self.login_flag:
            if not self.is_logged_in():
                self._login()

    def is_logged_in(self):
        title = self.find_element(
            By.XPATH, '/html/head/title').get_attribute('innerHTML')
        if title == "9GAG - 404 Nothing here":
            self.login_flag = False
            logger.debug("Detected you are NOT logged in")
            if self.attempted_login_flag:
                raise Exception("Wasn't able to login... Help")
            return False

        self.login_flag = True
        logger.debug("Detected you are logged in")
        return True

    def _login(self):
        logger.debug("Attempting to login")
        self.get(LOGIN_URL)
        time.sleep(1)
        username_field = self.find_element(
            By.CSS_SELECTOR, '#signup > form > div > div:nth-child(3) > input[type=text]') # noqa
        password_field = self.find_element(
            By.CSS_SELECTOR, '#signup > form > div > div:nth-child(4) > input[type=password]') # noqa
        username_field.clear()
        password_field.clear()
        username_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)
        login_button = self.find_element(
            By.CSS_SELECTOR,
            '#signup > form > div > button.ui-btn.btn-color-primary.login-view__login'  # noqa
        )
        login_button.click()
        time.sleep(1)
        self.attempted_login_flag = True
        self.is_logged_in()
        self.landing_page()

    @property
    def list_view(self):
        if not self._list_view_element:
            try:
                self._list_view_element = self.find_element(
                    By.CSS_SELECTOR,
                    '#list-view-2'
                )
            except NoSuchElementException:
                logger.warn(
                    "Unable to find list_view on page\n" +
                    self.page_source)
        return self._list_view_element

    def get_elements_from_stream(self, stream_no, raise_on_missing=False):

        try:
            stream: WebElement = self.list_view.find_element(
                By.CSS_SELECTOR,
                f'#stream-{stream_no}')
        except NoSuchElementException as e:
            if raise_on_missing:
                logger.warn(f"Unable to find stream {stream_no}" +
                            self.list_view.get_attribute('outerHTML')
                            )
                raise e

            logger.debug(f"Unable to find stream {stream_no}")
            return False

        try:
            articles = stream.find_elements(By.TAG_NAME, 'article')
        except NoSuchElementException as e:
            logger.warn('Unable to find articles in stream' +
                        stream.get_attribute('outerHTML')
                        )
            raise e

        elements = []

        for article in articles:

            try:
                try:
                    post_section = article.find_element(
                        By.CSS_SELECTOR,
                        'article > header > div > p > a.section'
                    ).get_attribute('innerHTML')
                except NoSuchElementException as e:
                    logger.warn('Unable to find post_section in article' +
                                article.get_attribute('outerHTML')
                                )
                    raise e

                if post_section == 'Promoted':
                    logger.debug("Skipping Promoted Post")
                    continue

                try:
                    title = article.find_element(
                        By.CSS_SELECTOR,
                        'article > header > a')
                except NoSuchElementException as e:
                    logger.warn('Unable to find title in article' +
                                article.get_attribute('outerHTML')
                                )
                    raise e

                title_name = title.text
                title_path = title.get_attribute('href')

                articledata = ArticleData(
                    title_name,
                    os.path.basename(title_path),
                    title_path,
                    post_section,
                    cover_photo=self.get_cover_photo(article)
                )
            except NoSuchElementException:
                logger.warn("Skipping Article because of missing element")
                continue

            elements.append(articledata)
        return elements

    def scroll(self, sleep=0.5, scroll=500):
        self.execute_script(f"window.scrollBy(0,{scroll})", "")
        time.sleep(sleep)

    def scroll_to_spinner(self, sleep=1):
        element = self.get_loader_element()
        actions = ActionChains(self)
        actions.move_to_element(element).perform()
        time.sleep(sleep)

    def get_cover_photo(self, article: WebElement):
        self.implicitly_wait(0)
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

        self.implicitly_wait(DEFAULT_IMPLICITY_WAIT)

        if not cover_photo:
            logger.warn("Unable to find cover photo\n" +
                        article.get_attribute('outerHTML')
                        )
            raise NoSuchElementException("Unable to find cover photo")

        return cover_photo

    def get_loader_element(self) -> WebElement:
        try:
            loader = self.list_view.find_element(
                By.CSS_SELECTOR, 'div.loading > a'
            )
        except NoSuchElementException as e:
            logger.warn('Unable to find loader in list_view' +
                        self.list_view.get_attribute('outerHTML')
                        )
            raise e
        return loader

    def is_loader_spinning(self):

        loader = self.get_loader_element().get_attribute('class')

        if "spin" in loader:
            return True
        elif "end" in loader:
            return False
        else:
            logger.warn('Unable to detect loader status' +
                        loader.get_attribute('outerHTML')
                        )
            raise Exception('Cannot detect loader')


@dataclass
class ArticleData:
    name: str
    id: str
    url: str
    post_section: str
    cover_photo: str

    def __post_init__(self):
        logger.debug(f"Created {self}")
