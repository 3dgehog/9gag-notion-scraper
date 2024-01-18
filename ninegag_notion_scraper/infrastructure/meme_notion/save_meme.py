"""A class that handles all the operations on Notion"""

import logging
from typing import Awaitable, Optional
from notion_client import Client, APIResponseError
from retry import retry

from ninegag_notion_scraper.app.entities.meme import DBMeme, PostMeme
from ninegag_notion_scraper.app.interfaces.repositories.meme \
    import SaveMemeRepo, UpdateMemeRepo

from .base import Properties, NotionBase
from .converters import PostIDConverter, PostTitleConverter, \
    PostURLConverter, PostTagsConverter, PostCoverURLConverter, TagsConverter


logger = logging.getLogger("app.notion")


class NotionSaveMeme(NotionBase, SaveMemeRepo, UpdateMemeRepo):
    def __init__(self, client: Client, database_id: str) -> None:
        NotionBase.__init__(self, client, database_id)

    def save_meme(self,
                  meme: PostMeme,
                  update: bool = False
                  ) -> None:
        title = meme.post_title
        item_id = meme.post_id
        external_web_url = meme.post_url
        tags = meme.post_tags
        cover_url = meme.post_cover_photo_url

        if not (existing_page := self._exists(item_id)):
            self._create_page(title, item_id, external_web_url,
                              tags, cover_url)
            logger.debug("Created page for Post ID of %s", item_id)

        elif existing_page and update:
            self._update_page(existing_page['id'], title, item_id,
                              external_web_url, tags, cover_url)
            logger.debug("Updated page for Post ID of %s", item_id)

    def meme_exists(self, meme: PostMeme | DBMeme) -> bool:
        return all([self._exists(meme.post_id)])

    def update_meme(self, id: str, tags: list) -> None:
        self._client.pages.update(
            page_id=id,
            properties={
                **TagsConverter.encode(tags)
            }
        )

    @retry(exceptions=APIResponseError, tries=5, delay=30, backoff=2)
    def _exists(self, post_id: str) -> Optional[dict]:
        """Checks if item with post_id exists and return if it does

        Args:
            post_id (str): post_id on notion

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
                    "equals": post_id
                }
            })

        assert not isinstance(query, Awaitable)
        results: list = query.get('results')

        if len(results) > 1:
            raise ValueError(f"More then 1 item has the id of {post_id}")
        if len(results) == 1:
            logger.debug("ID %s already exists", post_id)
            return results[0]
        logger.debug("ID %s doesn't exists", post_id)
        return None

    def _update_page(self, page_id, name, post_id, url, post_section,
                     cover_photo):
        self._client.pages.update(
            page_id=page_id,
            cover=PostCoverURLConverter.encode(cover_photo),
            properties={
                **PostTitleConverter.encode(name),
                **PostURLConverter.encode(url),
                **PostIDConverter.encode(post_id),
                **PostTagsConverter.encode(post_section)
            }
        )

    @retry(exceptions=APIResponseError, tries=5, delay=30, backoff=2)
    def _create_page(self, name, post_id, url, post_section, cover_photo):
        self._client.pages.create(
            parent={"database_id": self._db_id},
            cover=PostCoverURLConverter.encode(cover_photo),
            properties={
                **PostTitleConverter.encode(name),
                **PostURLConverter.encode(url),
                **PostIDConverter.encode(post_id),
                **PostTagsConverter.encode(post_section)
            }
        )
