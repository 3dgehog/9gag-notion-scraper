from selenium import webdriver
from latest_user_agents import get_latest_user_agents


def get_webbrowser_brave_locally_mac():
    brave_options = webdriver.ChromeOptions()

    brave_options.binary_location = \
        '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'

    WEB_DRIVER = webdriver.Chrome(options=brave_options)

    return WEB_DRIVER


def get_webdriver_firefox_remote(url: str):
    def get_webbroswer():
        firefox_options = webdriver.FirefoxOptions()

        firefox_options.add_argument(
            f"user-agent={get_latest_user_agents()[1]}")

        WEB_DRIVER = webdriver.Remote(
            command_executor=url,
            options=firefox_options
        )
        return WEB_DRIVER

    return get_webbroswer


def get_webbrowser_firefox_locally():
    firefox_options = webdriver.FirefoxOptions()

    firefox_options.add_argument(
        f"user-agent={get_latest_user_agents()[1]}")

    WEB_DRIVER = webdriver.Firefox(options=firefox_options)

    return WEB_DRIVER
