"""The main function"""

import logging
from notion_client import Client as NotionClient
from selenium.webdriver.remote.webdriver import WebDriver

# Setup tools
from .env import Environments, get_envs
from .cli import Arguments, get_args
from .webdriver import WEB_DRIVER

from .app.entities.meme import Meme
from .app.use_cases.cookies import CookiesUseCase
from .app.use_cases.get_memes import GetMemes
from .app.use_cases.save_meme import SaveMeme
from .infrastructure.cookie_filestorage \
    import FileCookiesRepo
from .infrastructure.meme_ninegag_scraper import NineGagScraperRepo
from .infrastructure.meme_notion import NotionStorageRepo
from .infrastructure.meme_filestorage import FileStorageRepo

logger = logging.getLogger('app')


def main(args: Arguments, envs: Environments, webdriver: WebDriver):
    """The entry point to the application"""

    cookie_usecase = CookiesUseCase(FileCookiesRepo())

    ninegag_repo = NineGagScraperRepo(
        envs.NINEGAG_URL,
        envs.NINEGAG_USERNAME,
        envs.NINEGAG_PASSWORD,
        webdriver,
        cookie_usecase
    )

    notion_repo = NotionStorageRepo(NotionClient(
        auth=envs.NOTION_TOKEN), envs.NOTION_DATABASE
    )

    filestorage_repo = FileStorageRepo(
        covers_path=envs.COVERS_PATH,
        memes_path=envs.MEMES_PATH,
        _selenium_cookies_func=cookie_usecase.get_cookies
    )

    memes_from_9gag_to_notion_with_local_save(
        GetMemes(ninegag_repo),
        SaveMeme(notion_repo),
        SaveMeme(filestorage_repo),
        args=args
    )


class StopLoopException(Exception):
    pass


def memes_from_9gag_to_notion_with_local_save(
        ninegag_scraper: GetMemes,
        notion: SaveMeme,
        file_storage: SaveMeme,
        args: Arguments) -> None:

    for memes in ninegag_scraper.get_memes():
        try:
            for meme in memes:
                try:
                    evaluate_storage(args, meme, file_storage)
                    evaluate_storage(args, meme, notion)
                except StopLoopException:
                    raise  # propagate the exception to stop the outer loop

        except StopLoopException:
            logger.debug("Loop stopped by evaluate_storage")


def evaluate_storage(args: Arguments,
                     meme: Meme,
                     storage: SaveMeme):

    exists = storage.meme_exists(meme)

    if args.skip_existing and exists:
        logger.info(f"Meme ID {meme.item_id} was skipped "
                    f"in '{storage.__class__.__name__}' because it "
                    "already exists")
        return

    if args.stop_existing and exists:
        raise StopLoopException  # stop the outer loop

    storage.save_meme(meme)


if __name__ == '__main__':
    args = get_args()
    envs = get_envs()
    main(args=args, envs=envs, webdriver=WEB_DRIVER)
