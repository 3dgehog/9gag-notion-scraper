"""The main function"""

import os
import logging
from typing import List
from notion_client import Client as NotionClient

from .scrapers.repository import AbstractScraperRepo
from .scrapers.repository.ninegag import NineGagScraperRepo
from .scrapers.entities import Meme
from .storage.repository import AbstractStorageRepo
from .storage.repository.notion import NotionStorageRepo
from .storage.repository.file_storage import FileStorageRepo

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DATABASE = os.environ["NOTION_DATABASE"]

NINEGAG_USERNAME = os.environ['USERNAME']
NINEGAG_PASSWORD = os.environ['PASSWORD']
NINEGAG_URL = os.environ['9GAG_URL']

PERSONAL_URL = "172.30.0.10:5000/WebDAV/9gag-memes"

logger = logging.getLogger('app')


def main():
    """The entry point to the application"""
    memes_from_9gag_to_notion_with_local_save(
        NineGagScraperRepo(NINEGAG_URL, NINEGAG_USERNAME, NINEGAG_PASSWORD),
        NotionStorageRepo(NotionClient(auth=NOTION_TOKEN), NOTION_DATABASE),
        FileStorageRepo("./dump")
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
    main()
