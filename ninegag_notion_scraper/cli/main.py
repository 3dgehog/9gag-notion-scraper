"""Main entry point for the CLI application"""

import logging
import time
from typing import Callable
from selenium.webdriver.remote.webdriver import WebDriver
from notion_client import Client as NotionClient

from ..env import get_envs, Environments
from ..args import get_args, Arguments
from ..use_cases.cookies import get_cookies
from ..use_cases.meme import GetPostMemes, SavePostMeme
from ..workflows import ScrapeNineGagToNotionAndStorageWorkflow
from ..adapters.repositories.cookie_filestorage import FileCookiesRepo
from ..adapters.repositories.meme_ninegag_scraper import \
    NineGagStreamScraperRepo
from ..adapters.repositories.meme_notion import NotionSaveMeme
from ..adapters.repositories.meme_filestorage import FileStorageRepo
from ..use_cases.webdriver import UseWebDriverContainer, select_webdriver
from .runners import run_notion_to_local

logger = logging.getLogger('app')


def main(
    args: Arguments,
    envs: Environments,
    get_webdriver: Callable[[], WebDriver]
) -> None:
    """The entry point to the application"""
    cookie_repo = FileCookiesRepo()
    with UseWebDriverContainer(get_webdriver()) as webdriver:
        if args.save_notion_meme_locally:
            run_notion_to_local(args, envs, webdriver, cookie_repo)
            quit()

        # Initialize repositories
        ninegag_scraper_repo = NineGagStreamScraperRepo(
            envs.NINEGAG_URL,
            envs.NINEGAG_USERNAME,
            envs.NINEGAG_PASSWORD,
            webdriver,
            cookie_repo
        )
        notion_storage_repo = NotionSaveMeme(
            NotionClient(auth=envs.NOTION_TOKEN), envs.NOTION_DATABASE
        )
        filestorage_repo = FileStorageRepo(
            covers_path=envs.COVERS_PATH,
            memes_path=envs.MEMES_PATH,
            _selenium_cookies_func=lambda: get_cookies(cookie_repo)
        )

        # Initialize and execute the use case
        scrape_usecase = ScrapeNineGagToNotionAndStorageWorkflow(
            get_post_memes=GetPostMemes(ninegag_scraper_repo),
            save_to_notion=SavePostMeme(notion_storage_repo),
            save_to_filestorage=SavePostMeme(filestorage_repo),
            args=args
        )
        scrape_usecase.execute()


def run():
    """Parse arguments, configure logging, and run the main application"""
    args = get_args()
    envs = get_envs()
    logger.setLevel(envs.LOG_LEVEL)
    logger.debug(f"Log level set to {envs.LOG_LEVEL}")
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode is ON")
    get_web_browser = select_webdriver(envs)
    if envs.RUN_INTERVAL_SECONDS != '0':
        logger.info(f"Running every {envs.RUN_INTERVAL_SECONDS} seconds")
        while True:
            try:
                main(args, envs, get_web_browser)
                time.sleep(int(envs.RUN_INTERVAL_SECONDS))
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received, exiting...")
                break
            except Exception as e:
                logger.error(f"An error occurred: {e}", exc_info=True)
                time.sleep(int(envs.RUN_INTERVAL_SECONDS))
                break
    else:
        main(args, envs, get_web_browser)
