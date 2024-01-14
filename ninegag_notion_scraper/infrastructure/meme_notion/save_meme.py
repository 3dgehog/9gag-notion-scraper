"""A class that handles all the operations on Notion"""

import logging
from typing import Awaitable, Optional
from notion_client import Client, APIResponseError
from retry import retry

from ninegag_notion_scraper.app.entities.meme import Meme
from ninegag_notion_scraper.app.interfaces.repositories.meme \
    import SaveMemeRepo

from .base import Properties, NotionBase
from .converters import ItemIDConverter, PageNameConverter, PostURLConverter, \
    TagsConverter, CoverURLConverter


logger = logging.getLogger("app.notion")


class NotionSaveMeme(NotionBase, SaveMemeRepo):
    def __init__(self, client: Client, database_id: str) -> None:
        NotionBase.__init__(self, client, database_id)

    def save_meme(self,
                  meme: Meme,
                  update: bool = False
                  ) -> None:
        title = meme.title
        item_id = meme.item_id
        external_web_url = meme.post_web_url
        tags = meme.tags
        cover_url = meme.cover_photo_url

        if not (existing_page := self._exists(item_id)):
            self._create_page(title, item_id, external_web_url,
                              tags, cover_url)
            logger.debug("Created page for Post ID of %s", item_id)

        elif existing_page and update:
            self._update_page(existing_page['id'], title, item_id,
                              external_web_url, tags, cover_url)
            logger.debug("Updated page for Post ID of %s", item_id)

    def meme_exists(self, meme: Meme) -> bool:
        return all([self._exists(meme.item_id)])

    @retry(exceptions=APIResponseError, tries=5, delay=30, backoff=2)
    def _exists(self, item_id: str) -> Optional[dict]:
        """Checks if item with item_id exists and return if it does

        Args:
            item_id (str): item_id on notion

        Raises:
            ValueError: More than 1 item with the same id was found

        Returns:
            Optional[dict]: page information from notion
        """
        query = self._client.databases.query(
            database_id=self._db_id,
            filter={
                "property": Properties.EXTERNAL_REF.value['name'],
                "rich_text": {
                    "equals": item_id
                }
            })

        assert not isinstance(query, Awaitable)
        results: list = query.get('results')

        if len(results) > 1:
            raise ValueError(f"More then 1 item has the id of {item_id}")
        if len(results) == 1:
            logger.debug("ID %s already exists", item_id)
            return results[0]
        logger.debug("ID %s doesn't exists", item_id)
        return None

    def _update_page(self, page_id, name, item_id, url, post_section,
                     cover_photo):
        self._client.pages.update(
            page_id=page_id,
            cover=CoverURLConverter.encode(cover_photo),
            properties={
                **PageNameConverter.encode(name),
                **PostURLConverter.encode(url),
                **ItemIDConverter.encode(item_id),
                **TagsConverter.encode(post_section)
            }
        )

    @retry(exceptions=APIResponseError, tries=5, delay=30, backoff=2)
    def _create_page(self, name, item_id, url, post_section, cover_photo):
        self._client.pages.create(
            parent={"database_id": self._db_id},
            cover=CoverURLConverter.encode(cover_photo),
            properties={
                **PageNameConverter.encode(name),
                **PostURLConverter.encode(url),
                **ItemIDConverter.encode(item_id),
                **TagsConverter.encode(post_section)
            }
        )
