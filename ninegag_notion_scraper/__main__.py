"""The main function"""

import os
import logging
from typing import List, Optional, Protocol
from notion_client import Client as NotionClient

from .scrapers.ninegag import NineGagTools
from .storage.notion import NotionTools
from .storage.file_storage import FileStorage
from .entities import Meme

os.environ['PATH'] += r":/Users/maxence/Projects/9gag-notion-scraper"

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DATABASE = os.environ["NOTION_DATABASE"]

NINEGAG_USERNAME = os.environ['USERNAME']
NINEGAG_PASSWORD = os.environ['PASSWORD']
NINEGAG_URL = os.environ['9GAG_URL']

PERSONAL_URL = "172.30.0.10:5000/WebDAV/9gag-memes"

logger = logging.getLogger('app')


class MemeScrapperProtocol(Protocol):
    """Protocol for interaction needed on the meme site"""
    at_bottom_flag: bool

    def __init__(self, root_url: str, username: str,
                 password: str) -> None: ...

    def __enter__(self): ...

    def __exit__(self, exception_type, exception_value, traceback): ...

    def get_memes(self) -> List[Meme]:
        """Get all memes from the current place on the page"""

    def next_page(self) -> Optional[int]:
        """Goes to the next set of memes"""


class MemeStorageProtocol(Protocol):
    def save_meme(self, meme: Meme, **kwargs) -> None: ...


def main():
    """The entry point to the application"""
    memes_from_9gag_to_notion_with_local_save(
        NineGagTools(NINEGAG_URL, NINEGAG_USERNAME, NINEGAG_PASSWORD),
        NotionTools(NotionClient(auth=NOTION_TOKEN), NOTION_DATABASE),
        FileStorage("./dump")
    )


def memes_from_9gag_to_notion_with_local_save(
        ninegag: MemeScrapperProtocol,
        notion: MemeStorageProtocol,
        storage: MemeStorageProtocol) -> None:

    with ninegag:

        memes: List[Meme]

        # Waiting until next stream is detected or the spinner ends
        while not ninegag.at_bottom_flag:
            memes = ninegag.get_memes()

            for meme in memes:
                storage.save_meme(meme)
                notion.save_meme(meme, options={"update": True})
            ninegag.next_page()


if __name__ == '__main__':
    main()
