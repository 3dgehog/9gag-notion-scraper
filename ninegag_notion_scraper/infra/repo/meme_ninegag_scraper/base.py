import time
import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver

from ninegag_notion_scraper.app.use_cases.cookies import CookiesUseCase

logger = logging.getLogger('app.9gag')


class ScraperNotSetup(Exception):
    pass


class BaseScraperRepo:
    def __init__(self,
                 username: str, password: str,
                 web_driver: WebDriver,
                 cookie_usecase: CookiesUseCase,
                 **kwargs) -> None:
        self.username = username
        self.password = password
        self.web_driver = web_driver
        self.at_end = False
        self.cookie_manager = cookie_usecase
        self.sleep = kwargs.get('sleep') or 0.5
        self.default_implicity_wait = kwargs.get(
            'default_implicity_wait') or 1

        self._login_flag = False
        self._attempted_login_flag = False
        self._login_url = 'https://9gag.com/login'
        self._homepage_url = 'https://9gag.com/'
        self._is_setup = False

        self.web_driver.implicitly_wait(self.default_implicity_wait)

    def get_cookies(self):
        return self.web_driver.get_cookies()

    def __enter__(self):
        self._setup()
        self._is_setup = True
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._is_setup = False
        self.web_driver.quit()

    def _setup(self):
        url = self._homepage_url
        self.web_driver.get(url)
        self._load_cookies()
        self.web_driver.get(url)

        self._accept_cookie_dialog()

        if not self._login_flag:
            if not self._is_logged_in():
                self._login()
                self.web_driver.get(url)

    def _load_cookies(self):
        if (cookies := self.cookie_manager.get_cookies()):
            for cookie in cookies:
                self.web_driver.add_cookie(cookie)

    def _accept_cookie_dialog(self):
        try:
            dialog = self.web_driver.find_element(
                By.CSS_SELECTOR, '#qc-cmp2-ui')
        except NoSuchElementException:
            return

        accept_button = dialog.find_element(
            By.CSS_SELECTOR,
            'div.qc-cmp2-footer.qc-cmp2-footer-overlay.qc-cmp2-footer-scrolled'
            ' > div > button.css-1k47zha')
        accept_button.click()

    def _is_logged_in(self):
        title_based = self.web_driver.find_element(
            By.XPATH, '/html/head/title').get_attribute('innerHTML')
        if title_based == "9GAG - 404 Nothing here":
            self._login_flag = False
            logger.debug("Detected you are NOT logged in")
            if self._attempted_login_flag:
                raise RuntimeError("Wasn't able to login... Help")
            return False
        top_nav_based = self.web_driver.find_element(
            By.CSS_SELECTOR,
            '#top-nav > div > div > '
            'div.visitor-function').get_attribute('style')
        if top_nav_based == "":
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
        self.web_driver.get(self._login_url)

        time.sleep(self.sleep)

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
            '#signup > form > div > button.ui-btn.'
            'btn-color-primary.login-view__login'
        )

        login_button.click()

        time.sleep(self.sleep)

        self._attempted_login_flag = True

        self._is_logged_in()

        self.cookie_manager.save_cookies(self.web_driver.get_cookies())
