"""Main entry point for the CLI application"""

import logging
import time
from typing import Callable
from selenium.webdriver.remote.webdriver import WebDriver

from ..env import get_envs, Environments
from ..args import get_args, Arguments
from ..use_cases.cookies import CookiesUseCase
from ..adapters.repositories.cookie_filestorage import FileCookiesRepo
from .container import WebDriverContainer, select_webdriver
from .runners import run_notion_to_local, run_9gag_to_notion

logger = logging.getLogger('app')


def main(
    args: Arguments,
    envs: Environments,
    get_webdriver: Callable[[], WebDriver]
) -> None:
    """The entry point to the application"""
    cookie_usecase = CookiesUseCase(FileCookiesRepo())
    with WebDriverContainer(get_webdriver()) as webdriver:
        if args.save_notion_meme_locally:
            run_notion_to_local(args, envs, webdriver, cookie_usecase)
        run_9gag_to_notion(args, envs, webdriver, cookie_usecase)


def run():
    """Parse arguments, configure logging, and run the main application"""
    args = get_args()
    envs = get_envs()
    logger.setLevel(envs.LOG_LEVEL)
    logger.debug(f"Log level set to {envs.LOG_LEVEL}")
    if args.debug:
        pass
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
    else:
        main(args, envs, get_web_browser)
