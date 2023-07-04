import os
from dataclasses import dataclass
from urllib.request import urlretrieve
from urllib.parse import urlparse
import validators
import requests
from ninegag_notion_scraper.entities import Meme

COVERS_PATH = "covers"
MEME_PATH = "memes"


@dataclass
class URLItems:
    file_name: str
    file_extension: str


class FileStorage:
    """A class to save items locally on the file system"""

    def __init__(self, path: str) -> None:
        self._path = path
        self._meme_path = os.path.join(self._path, MEME_PATH)
        self._covers_path = os.path.join(self._path, COVERS_PATH)

    def save_meme(self, meme: Meme) -> None:
        self._save_cover_from_url(meme.cover_photo_url, meme.item_id)
        self._save_meme_from_url(meme.post_file_url, meme.item_id)

    def _save_meme_from_url(self, url: str, file_id: str):
        """Save memes from a url"""
        self._validate_url(url)
        url_item = self._url_items(url)
        urlretrieve(url, os.path.join(self._meme_path,
                    file_id + url_item.file_extension))

    def _save_cover_from_url(self, url: str, file_id: str):
        """Save covers from a url"""
        self._validate_url(url)
        url_item = self._url_items(url)
        # urlretrieve(url, os.path.join(self._covers_path,
        #             file_id + url_item.file_extension))
        req = requests.get(url, allow_redirects=True, timeout=60)
        with open(os.path.join(self._covers_path, file_id +
                               url_item.file_extension), 'wb') as file:
            file.write(req.content)

    def _validate_url(self, url: str) -> None:
        if not validators.url(url):
            raise ValueError("Value passed is not a url")

    def _url_items(self, url: str) -> URLItems:
        url_parse = urlparse(url)
        file_path, file_ext = os.path.splitext(url_parse.path)
        return URLItems(file_path.split('/')[-1], file_ext)
