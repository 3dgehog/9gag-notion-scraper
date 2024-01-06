"""The main function"""

from argparse import Namespace
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


def main(args: Namespace, envs: Environments, webdriver: WebDriver):
    """The entry point to the application"""

    if args.skip_existing:
        pass

    memes_from_9gag_to_notion_with_local_save(
        NineGagScraperRepo(envs.NINEGAG_URL, envs.NINEGAG_USERNAME,
                           envs.NINEGAG_PASSWORD, webdriver),
        NotionStorageRepo(NotionClient(
            auth=envs.NOTION_TOKEN), envs.NOTION_DATABASE),
        FileStorageRepo(covers_path=envs.COVERS_PATH,
                        memes_path=envs.MEMES_PATH)
    )


def memes_from_9gag_to_notion_with_local_save(
        ninegag: AbstractScraperRepo,
        notion: AbstractStorageRepo,
        storage: AbstractStorageRepo) -> None:

    with ninegag:

        memes: List[Meme]

        # Waiting until next stream is detected or the spinner ends
        while not ninegag.at_bottom:
            memes = ninegag.get_memes()

            for meme in memes:
                storage.save_meme(meme)
                notion.save_meme(meme, update=True)
            ninegag.next_page()


if __name__ == '__main__':
    args = get_args()
    envs = get_envs()
    main(args=args, envs=envs, webdriver=WEB_DRIVER)
