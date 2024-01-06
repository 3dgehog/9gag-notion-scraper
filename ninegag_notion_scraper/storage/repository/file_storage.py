import os
from dataclasses import dataclass
from urllib.request import urlretrieve
from urllib.parse import urlparse
import validators
import requests
import glob
import logging

from ninegag_notion_scraper.scrapers.entities import Meme
from . import AbstractStorageRepo


logger = logging.getLogger('app.storage')


@dataclass
class URLItem:
    file_name: str
    file_extension: str


class FileStorageRepo(AbstractStorageRepo):
    """A class to save items locally on the file system"""

    def __init__(self, covers_path: str, memes_path: str) -> None:
        self.meme_path = memes_path
        self.covers_path = covers_path

    def save_meme(self, meme: Meme, *args) -> None:
        self._save_cover_from_url(meme.cover_photo_url, meme.item_id)
        self._save_meme_from_url(meme.post_file_url, meme.item_id)

    def meme_exists(self, meme: Meme) -> bool:
        logger.debug(f"Checking if meme {meme.item_id} exists")
        meme_exists = glob.glob(
            os.path.join(self.meme_path, f"{meme.item_id}.*")
        )
        cover_exists = glob.glob(
            os.path.join(self.covers_path, f"{meme.item_id}.*")
        )
        return all([meme_exists, cover_exists])

    def _save_meme_from_url(self, url: str, file_id: str):
        """Save memes from a url"""
        self._validate_url(url)
        url_item = self._get_url_items_from_url(url)
        urlretrieve(url, os.path.join(self.meme_path,
                    file_id + url_item.file_extension))
        logger.debug(f"Post file: '{file_id + url_item.file_extension}'"
                     f" saved in: '{self.meme_path}'")

    def _save_cover_from_url(self, url: str, file_id: str):
        """Save covers from a url"""
        self._validate_url(url)
        url_item = self._get_url_items_from_url(url)
        # urlretrieve(url, os.path.join(self._covers_path,
        #             file_id + url_item.file_extension))
        req = requests.get(url, allow_redirects=True, timeout=60)
        with open(os.path.join(self.covers_path, file_id +
                               url_item.file_extension), 'wb') as file:
            file.write(req.content)
        logger.debug(f"Post cover: '{file_id + url_item.file_extension}'"
                     f" saved in: '{self.covers_path}'")

    def _validate_url(self, url: str) -> None:
        if not validators.url(url):
            raise ValueError("Value passed is not a url")

    def _get_url_items_from_url(self, url: str) -> URLItem:
        url_parse = urlparse(url)
        file_path, file_ext = os.path.splitext(url_parse.path)
        return URLItem(file_path.split('/')[-1], file_ext)
