"""A class that handles all the operations on Notion"""

from enum import Enum
import logging
from typing import Awaitable, Optional
from notion_client import Client
from retry import retry

from ninegag_notion_scraper.scrapers.entities import Meme
from . import AbstractStorageRepo


logger = logging.getLogger("app.notion")


class Properties(Enum):
    EXTERNAL_REF = {"name": "9gag id", "type": "rich_text"}
    EXTERNAL_URL = {"name": "URL", "type": "url"}
    TAGS = {"name": "Post Section", "type": "multi_select"}


class NotionStorageRepo(AbstractStorageRepo):
    def __init__(self, client: Client, database_id: str) -> None:
        self._client = client
        self._db_id = database_id
        self._validate_database_schema(database_id)

    def save_meme(self, meme: Meme, update: bool = False) -> None:
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

    def _validate_database_schema(self, database_id: str) -> None:
        db = self._client.databases.retrieve(database_id)
        assert isinstance(db, dict)

        def compare_dictionaries(dict1, dict2):
            for key, value in dict2.items():
                if key not in dict1 or dict1[key] != value:
                    return False
            return True

        # Validate if all Properties exists in database
        for enum_item_dict in [x.value for x in Properties]:
            valid = False
            for db_prop_dict in list(db["properties"].values()):
                if compare_dictionaries(db_prop_dict, enum_item_dict):
                    valid = True
                    break
            if not valid:
                raise ValueError(
                    f"Property {enum_item_dict} is missing in database")

    @retry(exceptions=Exception, tries=5, delay=30, backoff=2)
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

    def _validate_multi_select(self, data: str) -> str:
        # commas create problems so the are replaced with nothing
        return data.replace(',', '')

    def _expand_multi_select(self, data: list) -> list:
        """
        splits item list to object list to support creating multi selection
        on notion
        """
        return [{"name": self._validate_multi_select(x)} for x in data]

    def _update_page(self, page_id, name, item_id, url, post_section,
                     cover_photo):
        self._client.pages.update(
            page_id=page_id,
            cover=self._create_notion_json_for_cover(cover_photo),
            properties=self._create_notion_json_for_all_properties(
                name, url, item_id, post_section)
        )

    @retry(exceptions=Exception, tries=5, delay=30, backoff=2)
    def _create_page(self, name, item_id, url, post_section, cover_photo):
        self._client.pages.create(
            parent={"database_id": self._db_id},
            cover=self._create_notion_json_for_cover(cover_photo),
            properties=self._create_notion_json_for_all_properties(
                name, url, item_id, post_section)
        )

    def _create_notion_json_for_cover(self, url: str):
        return {
            "type": "external",
            "external": {
                    "url": url
            }
        }

    def _create_notion_json_for_all_properties(
            self, name, url, item_id, post_section):
        return {
            "Name": self._create_notion_json_for_name(name),

            Properties.EXTERNAL_URL.value['name']:
            self._create_notion_json_for_external_url(url),

            Properties.EXTERNAL_REF.value['name']:
            self._create_notion_json_for_external_ref(item_id),

            Properties.TAGS.value['name']:
            self._create_notion_json_for_tags(post_section)
        }

    def _create_notion_json_for_name(self, name: str):
        return {
            "title": [{
                "text": {
                    "content": name
                }
            }]
        }

    def _create_notion_json_for_external_url(self, url: str):
        return {"url": url}

    def _create_notion_json_for_external_ref(self, item_id: str):
        return {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": item_id
                }
            }]
        }

    def _create_notion_json_for_tags(self, tags: list):
        return {
            "multi_select": self._expand_multi_select(tags)
        }


class MaxRetryError(Exception):
    """An Error raised when the app reaches the max retries amount"""
