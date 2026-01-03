"""Dependency container and WebDriver management"""

import logging
from typing import Callable
from selenium.webdriver.remote.webdriver import WebDriver

from ..env import Environments
from ..adapters.webdriver import \
    get_webdriver_firefox_remote, get_webbrowser_firefox_locally, \
    get_webbrowser_brave_locally_mac

logger = logging.getLogger('app')


class WebDriverContainer:
    """A container for the WebDriver instance"""

    def __init__(self, webdriver: WebDriver):
        logger.debug("Initializing WebDriver")
        self.webdriver = webdriver
        logger.debug("WebDriver initialized")

    def __enter__(self):
        return self.webdriver

    def __exit__(self, exc_type, exc_value, traceback):
        if self.webdriver:
            self.webdriver.quit()


def select_webdriver(envs: Environments) -> Callable[[], WebDriver]:
    """
    Selects and returns the appropriate webdriver getter based on environment.
    """
    match [envs.WEBDRIVER_URL, envs.BROWSER]:
        case ["", "firefox"]:
            logger.info("Using Local Firefox WebDriver")
            return get_webbrowser_firefox_locally
        case ["", "brave"]:
            logger.info("Using Local Brave WebDriver on macOS")
            return get_webbrowser_brave_locally_mac
        case [url, "firefox"]:
            logger.info(f"Using Remote Firefox WebDriver URL: {url}")
            return get_webdriver_firefox_remote(url)
        case _:
            logger.error(
                "Unsupported WebDriver configuration. "
                "Please check your environment variables."
            )
            raise ValueError("Unsupported WebDriver configuration")
