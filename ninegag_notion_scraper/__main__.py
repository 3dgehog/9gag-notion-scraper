"""The main function"""

from argparse import Namespace
import logging
from typing import List
from notion_client import Client as NotionClient
from selenium.webdriver.remote.webdriver import WebDriver


from .env import Environments, get_envs
from .cli import get_args
from .webdriver import WEB_DRIVER
from .scrapers.repository import AbstractScraperRepo
from .scrapers.repository.ninegag import NineGagScraperRepo
from .scrapers.entities import Meme
from .storage.repository import AbstractStorageRepo
from .storage.repository.notion import NotionStorageRepo
from .storage.repository.file_storage import FileStorageRepo

logger = logging.getLogger('app')


def main(args: Namespace, envs: Environments, webdriver: WebDriver):
    """The entry point to the application"""

    memes_from_9gag_to_notion_with_local_save(
        NineGagScraperRepo(envs.NINEGAG_URL, envs.NINEGAG_USERNAME,
                           envs.NINEGAG_PASSWORD, webdriver),
        NotionStorageRepo(NotionClient(
            auth=envs.NOTION_TOKEN), envs.NOTION_DATABASE),
        FileStorageRepo(covers_path=envs.COVERS_PATH,
                        memes_path=envs.MEMES_PATH),
        args=args
    )


class StopLoopException(Exception):
    pass


def memes_from_9gag_to_notion_with_local_save(
        ninegag: AbstractScraperRepo,
        notion: AbstractStorageRepo,
        file_storage: AbstractStorageRepo,
        args: Namespace) -> None:

    with ninegag:
        try:
            memes: List[Meme]

            while not ninegag.at_bottom:
                memes = ninegag.get_memes()

                for meme in memes:
                    try:
                        evaluate_storage(args, meme, file_storage)
                        evaluate_storage(args, meme, notion)
                    except StopLoopException:
                        raise  # propagate the exception to stop the outer loop

                ninegag.next_page()

        except StopLoopException:
            logger.debug("Loop stopped by evaluate_storage")


def evaluate_storage(args: Namespace,
                     meme: Meme,
                     storage: AbstractStorageRepo):

    exists = storage.meme_exists(meme)

    if args.skip_existing and exists:
        logger.info(f"Meme ID {meme.item_id} was skipped "
                    f"in '{storage.__class__.__name__}' because it "
                    "already exists")
        return

    if args.stop_existing and exists:
        raise StopLoopException  # stop the outer loop

    storage.save_meme(meme, update=True)


if __name__ == '__main__':
    args = get_args()
    envs = get_envs()
    main(args=args, envs=envs, webdriver=WEB_DRIVER)
