import time
import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, \
    UnableToSetCookieException
from selenium.webdriver.remote.webdriver import WebDriver

from ninegag_notion_scraper.use_cases.cookies import get_cookies, save_cookies
from ninegag_notion_scraper.domain.interfaces.repositories.cookie \
    import CookieRepo

logger = logging.getLogger('app.9gag')


class ScraperNotSetup(Exception):
    pass


class BaseScraperRepo:
    """
    This is the base class for 9gag scrapers. It handles login, cookie
    management, and initial setup.
    """
    def __init__(self,
                 username: str, password: str,
                 web_driver: WebDriver,
                 cookie_repo: CookieRepo,
                 **kwargs) -> None:
        self.username = username
        self.password = password
        self.web_driver = web_driver
        self.at_end = False
        self.cookie_repo = cookie_repo
        self.sleep = kwargs.get('sleep') or 0.5
        self.default_implicity_wait = kwargs.get(
            'default_implicity_wait') or 1

        self._login_flag = False
        self._attempted_login_flag = False
        self._login_url = 'https://9gag.com/login'
        self._homepage_url = 'https://9gag.com/'

        self.web_driver.implicitly_wait(self.default_implicity_wait)

        self._setup()

    def get_cookies(self):
        return self.web_driver.get_cookies()

    def _setup(self):
        url = self._homepage_url
        self.web_driver.get(url)
        self._load_cookies()
        self.web_driver.get(url)

        time.sleep(self.sleep)

        self._detect_and_handle_dialogs()

        time.sleep(self.sleep)

        if not self._login_flag:
            if not self._is_logged_in():
                self._login()
                self.web_driver.get(url)

    def _load_cookies(self):
        if (cookies := get_cookies(self.cookie_repo)):
            for cookie in cookies:
                try:
                    self.web_driver.add_cookie(cookie)
                except UnableToSetCookieException:
                    logger.warning(
                        f"Unable to set cookie: {cookie.get('name')}, "
                        "Skipping...")
                    continue

    def _detect_and_handle_dialogs(self):
        logger.debug("Detecting and handling dialogs if any")
        self._detect_and_accept_cookie_dialog()
        self._detect_and_accept_value_your_privacy_dialog()

    def _detect_and_accept_cookie_dialog(self):
        try:
            dialog = self.web_driver.find_element(
                By.CSS_SELECTOR, '#qc-cmp2-ui')
            logger.debug("Found Cookie Dialog")
        except NoSuchElementException:
            return

        accept_button = dialog.find_element(
            By.CSS_SELECTOR,
            'div.qc-cmp2-footer.qc-cmp2-footer-overlay.qc-cmp2-footer-scrolled'
            ' > div > button.css-1k47zha')
        logger.debug("Clicking Accept button on Cookie Dialog")
        accept_button.click()

    def _detect_and_accept_value_your_privacy_dialog(self):
        try:
            iframe_element = self.web_driver.find_element(
                By.CSS_SELECTOR, "iframe[id^='sp_message_iframe']")
            logger.debug("Found Value Your Privacy Dialog iFrame")

        except NoSuchElementException:
            return

        logger.debug("Switching to Value Yours Privacy Dialog iFrame")
        self.web_driver.switch_to.frame(iframe_element)

        try:
            accept_button = self.web_driver.find_element(
                By.CSS_SELECTOR,
                'button[aria-label="Accept"]'
            )
        except NoSuchElementException:
            logger.error(
                "Accept button not found in Value Yours Privacy Dialog")
            raise ScraperNotSetup(
                "Accept button not found in Value Yours Privacy Dialog")

        logger.debug("Clicking Accept button on Value Yours Privacy Dialog")
        accept_button.click()

        logger.debug("Switching back to default content")
        self.web_driver.switch_to.default_content()

    # Check if user is logged in
    def _is_logged_in(self):
        title = self.web_driver.find_element(
            By.XPATH, '/html/head/title').get_attribute('innerHTML')
        if title == "9GAG - 404 Nothing here":
            self._login_flag = False
            logger.debug("Detected you are NOT logged in")
            if self._attempted_login_flag:
                raise RuntimeError("Wasn't able to login... Help")
            return False

        top_nav = self.web_driver.find_element(
            By.CSS_SELECTOR,
            '#top-navb > div > div > '
            'div.visitor-function').get_attribute('style')
        if top_nav == "":
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

        try:
            username_field = self.web_driver.find_element(
                By.CSS_SELECTOR,
                '#signup > form > div > div:nth-child(3) > input[type=text]'
            )
        except NoSuchElementException:
            logger.error("Username field not found, login failed")
            raise ScraperNotSetup("Username field not found, login failed")

        try:
            password_field = self.web_driver.find_element(
                By.CSS_SELECTOR,
                '#signup > form > div > div:nth-child(4) > '
                'input[type=password]'
            )
        except NoSuchElementException:
            logger.error("Password field not found, login failed")
            raise ScraperNotSetup("Password field not found, login failed")

        logger.debug("Clearing Login Fields")
        username_field.clear()
        password_field.clear()

        logger.debug("Entering Login Credentials")
        username_field.send_keys(self.username)
        password_field.send_keys(self.password)

        try:
            login_button = self.web_driver.find_element(
                By.CSS_SELECTOR,
                '#signup > form > div > button.ui-btn.'
                'btn-color-primary.login-view__login'
            )
        except NoSuchElementException:
            logger.error("Login button not found, login failed")
            raise ScraperNotSetup("Login button not found, login failed")

        logger.debug("Clicking Login Button")
        login_button.click()

        time.sleep(self.sleep)

        self._attempted_login_flag = True

        self._is_logged_in()

        save_cookies(self.cookie_repo, self.get_cookies())
