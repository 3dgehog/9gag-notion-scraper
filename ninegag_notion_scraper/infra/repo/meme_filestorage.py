import os
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse
import validators
import requests
import glob
import logging

from ninegag_notion_scraper.app.entities.meme import DBMeme, PostMeme
from ninegag_notion_scraper.app.interfaces.meme_repo import SaveMemeRepo


logger = logging.getLogger('app.storage')


class DownloadError(Exception):
    pass


@dataclass
class URLItem:
    file_name: str
    file_extension: str


class FileStorageRepo(SaveMemeRepo):
    """A class to save items locally on the file system"""

    def __init__(self, covers_path: str,
                 memes_path: str, _selenium_cookies_func: Callable) -> None:
        self.meme_path = memes_path
        self.covers_path = covers_path

        # Request setup
        self._session = requests.Session()
        self._selenium_cookies_func = _selenium_cookies_func
        self._cookie_loaded_flag = False

    def save_meme(self, meme: PostMeme, update=False) -> None:
        if update:
            logger.warning("Kwarg 'update' is not implmented in this class")
        self._save_cover_from_url(meme.post_cover_photo_url, meme.post_id)
        assert meme.post_file_url
        self._save_meme_from_url(meme.post_file_url, meme.post_id)

    def meme_exists(self, meme: PostMeme | DBMeme) -> bool:
        logger.debug(f"Checking if meme {meme.post_id} exists")
        meme_exists = glob.glob(
            os.path.join(self.meme_path, f"{meme.post_id}.*")
        )
        cover_exists = glob.glob(
            os.path.join(self.covers_path, f"{meme.post_id}.*")
        )
        return all([meme_exists, cover_exists])

    @property
    def session(self) -> requests.Session:
        if not self._cookie_loaded_flag:
            self._load_cookies()
            self._cookie_loaded_flag = True
        return self._session

    def _load_cookies(self) -> None:
        for cookie in self._selenium_cookies_func():
            self._session.cookies.set(cookie['name'], cookie['value'])
        logger.debug("Cookies loaded")

    def _save_file_from_url_and_path(self, url: str, file_id: str, path: str):
        self._validate_url(url)
        url_item = self._get_url_items_from_url(url)
        response = self.session.get(url)
        destination_path = os.path.join(path,
                                        file_id + url_item.file_extension)

        if response.status_code == 200:
            with open(destination_path, 'wb') as file:
                file.write(response.content)
        else:
            raise DownloadError(
                "Failed to download file. Status code: "
                f"{response.status_code}")

        logger.debug(f"File: '{file_id + url_item.file_extension}'"
                     f" saved in: '{path}'")

    def _save_meme_from_url(self, url: str, file_id: str):
        return self._save_file_from_url_and_path(url,
                                                 file_id,
                                                 self.meme_path)

    def _save_cover_from_url(self, url: str, file_id: str):
        return self._save_file_from_url_and_path(url,
                                                 file_id,
                                                 self.covers_path)

    def _validate_url(self, url: str) -> None:
        if not validators.url(url):
            raise ValueError("Value passed is not a url")

    def _get_url_items_from_url(self, url: str) -> URLItem:
        url_parse = urlparse(url)
        file_path, file_ext = os.path.splitext(url_parse.path)
        return URLItem(file_path.split('/')[-1], file_ext)
