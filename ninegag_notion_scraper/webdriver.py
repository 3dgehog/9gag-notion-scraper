from selenium import webdriver
from latest_user_agents import get_latest_user_agents


def get_webdriver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()

    # Headless
    # if os.environ.get('HEADLESS'):
    #     chrome_options.add_argument('headless')

    chrome_options.add_argument(f"user-agent={get_latest_user_agents()[1]}")

    WEB_DRIVER = webdriver.Chrome(options=chrome_options)

    # WEB_DRIVER = webdriver.Remote(
    #     command_executor='http://172.30.0.4:4444',
    #     options=chrome_options
    # )

    return WEB_DRIVER
