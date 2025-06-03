"""The main function"""

import logging
import time
from typing import Callable
from notion_client import Client as NotionClient
from selenium.webdriver.remote.webdriver import WebDriver

from ninegag_notion_scraper.app.use_cases.meme import GetDBMemes, \
    GetPostMeme, GetPostMemes, SavePostMeme, UpdateMeme
from ninegag_notion_scraper.infra.repo.meme_ninegag_scraper.page_single \
    import Meme404, NineGagSinglePageScraperRepo
from ninegag_notion_scraper.infra.repo.meme_notion.get_memes \
    import NotionGetMemes

# Setup tools
from .env import Environments, get_envs
from .args import Arguments, get_args

from .infra.webdriver import \
    get_webdriver_firefox_remote, get_webbrowser_firefox_locally, \
    get_webbrowser_brave_locally_mac
from .app.entities.meme import PostMeme
from .app.use_cases.cookies import CookiesUseCase
from .infra.repo.cookie_filestorage \
    import FileCookiesRepo
from .infra.repo.meme_ninegag_scraper import NineGagStreamScraperRepo
from .infra.repo.meme_notion import NotionSaveMeme
from .infra.repo.meme_filestorage import FileStorageRepo

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


def main(args: Arguments, envs: Environments,
         get_webdriver: Callable[[], WebDriver]) -> None:
    """The entry point to the application"""

    cookie_usecase = CookiesUseCase(FileCookiesRepo())

    with WebDriverContainer(get_webdriver()) as webdriver:

        if args.save_notion_meme_locally:
            notion_client = NotionClient(auth=envs.NOTION_TOKEN)
            notion_get = NotionGetMemes(
                notion_client, envs.NOTION_DATABASE)
            notion_update = NotionSaveMeme(
                notion_client, envs.NOTION_DATABASE)
            file_storage = FileStorageRepo(
                covers_path=envs.COVERS_PATH,
                memes_path=envs.MEMES_PATH,
                _selenium_cookies_func=cookie_usecase.get_cookies
            )
            ninegag = NineGagSinglePageScraperRepo(
                envs.NINEGAG_USERNAME,
                envs.NINEGAG_PASSWORD,
                webdriver,
                cookie_usecase
            )
            memes_from_notion_to_save_locally(
                notion_get=GetDBMemes(notion_get),
                notion_update=UpdateMeme(notion_update),
                file_storage=SavePostMeme(file_storage),
                ninegag=GetPostMeme(ninegag),
                args=args
            )

        ninegag_scraper_repo = NineGagStreamScraperRepo(
            envs.NINEGAG_URL,
            envs.NINEGAG_USERNAME,
            envs.NINEGAG_PASSWORD,
            webdriver,
            cookie_usecase
        )

        notion_storage_repo = NotionSaveMeme(NotionClient(
            auth=envs.NOTION_TOKEN), envs.NOTION_DATABASE
        )

        filestorage_repo = FileStorageRepo(
            covers_path=envs.COVERS_PATH,
            memes_path=envs.MEMES_PATH,
            _selenium_cookies_func=cookie_usecase.get_cookies
        )

        memes_from_9gag_to_notion_with_local_save(
            ninegag=GetPostMemes(ninegag_scraper_repo),
            notion=SavePostMeme(notion_storage_repo),
            file_storage=SavePostMeme(filestorage_repo),
            args=args
        )


def memes_from_9gag_to_notion_with_local_save(
        ninegag: GetPostMemes,
        notion: SavePostMeme,
        file_storage: SavePostMeme,
        args: Arguments) -> None:

    logger.debug("Starting to scrape memes from 9GAG")

    should_stop = False
    for memes in ninegag.get_memes():
        for meme in memes:
            if evaluate_storage(args, meme, file_storage):
                should_stop = True
                break
            if evaluate_storage(args, meme, notion):
                should_stop = True
                break
        if should_stop:
            logger.debug("Loop stopped by evaluate_storage")
            break


def evaluate_storage(args: Arguments,
                     meme: PostMeme,
                     storage: SavePostMeme):
    exists = storage.meme_exists(meme)

    if args.skip_existing and exists:
        logger.info(f"Meme ID {meme.post_id} was skipped "
                    f"in '{storage.__class__.__name__}' because it "
                    "already exists")
        return False

    if not args.ignore_existing and exists:
        return True  # signal to stop the outer loop

    storage.save_meme(meme)
    return False


def memes_from_notion_to_save_locally(
        notion_get: GetDBMemes,
        notion_update: UpdateMeme,
        file_storage: SavePostMeme,
        ninegag: GetPostMeme,
        args: Arguments
):
    logger.debug("Starting to scrape memes from Notion")

    filter = {
        "property": "Tags",
        "multi_select": {
            "does_not_contain": "Meme404"
        }
    }

    should_stop = False
    for memes in notion_get.get_memes(filter=filter):
        for meme in memes:
            if not file_storage.meme_exists(meme):
                logger.info(f"Meme {meme.post_id} doesn't exists locally")

                try:
                    loaded_meme = ninegag.get_meme_from_url(
                        meme.post_url)
                except Meme404:
                    logger.info(
                        f"skipping Meme ID {meme.post_id} because it "
                        "doesn't exist anymore")
                    notion_update.update_meme(meme.id, tags=['Meme404'])
                    continue

                if evaluate_storage(args, loaded_meme, file_storage):
                    should_stop = True
                    break
            else:
                logger.info(f"Meme {meme.post_id} already exists")
        if should_stop:
            logger.debug("Loop stopped by evaluate_storage")
            break


if __name__ == '__main__':
    args = get_args()
    envs = get_envs()

    logger.setLevel(envs.LOG_LEVEL)
    logger.debug(f"Log level set to {envs.LOG_LEVEL}")

    if args.debug:
        # from .debug import main as debug
        # debug(args, envs)
        # quit()
        pass

    match [envs.WEBDRIVER_URL, envs.BROWSER]:
        case ["", "firefox"]:
            logger.info("Using Local Firefox WebDriver")
            get_web_browser = get_webbrowser_firefox_locally
        case ["", "brave"]:
            logger.info("Using Local Brave WebDriver on macOS")
            get_web_browser = get_webbrowser_brave_locally_mac
        case [url, "firefox"]:
            logger.info(f"Using Remote Firefox WebDriver URL: {url}")
            get_web_browser = get_webdriver_firefox_remote(url)
        case _:
            logger.error("Unsupported WebDriver configuration. "
                         "Please check your environment variables.")
            raise ValueError("Unsupported WebDriver configuration")

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
