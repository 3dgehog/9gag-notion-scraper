"""A class that handles all the operations on Notion"""

from enum import Enum
import logging
import time
import traceback
from typing import Awaitable, Optional
from notion_client import Client

from ninegag_notion_scraper.entities import Meme


logger = logging.getLogger("app.notion")


class Properties(Enum):
    EXTERNAL_REF = {"name": "9gag id", "type": "rich_text"}
    EXTERNAL_URL = {"name": "URL", "type": "url"}
    TAGS = {"name": "Post Section", "type": "multi_select"}


class NotionTools:
    def __init__(self, client: Client, database_id: str) -> None:
        self._client = client
        self._db_id = database_id
        self._validate_database(database_id)

    def _validate_database(self, database_id: str) -> None:
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
            for db_prop_dict in [x for x in db["properties"].values()]:
                if compare_dictionaries(db_prop_dict, enum_item_dict):
                    valid = True
                    break
            if not valid:
                raise ValueError(
                    f"Property {enum_item_dict} is missing in database")

    def exists(self, item_id: str) -> bool:
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

        if len(results) >= 1:
            logger.debug("ID %s already exists", item_id)
            return True
        logger.debug("ID %s doesn't exists", item_id)
        return False

    def _validate_multi_select(self, data: str) -> str:
        return data.replace(',', '')

    def _expand_multi_select(self, data: list) -> list:
        return [{"name": self._validate_multi_select(x)} for x in data]

    def _create_page(self, name, item_id, url, post_section, cover_photo):
        self._client.pages.create(
            parent={"database_id": self._db_id},
            cover={
                "type": "external",
                "external": {
                        "url": cover_photo
                }
            },
            properties={
                "Name": {
                    "title": [{
                        "text": {
                            "content": name
                        }
                    }]
                },
                Properties.EXTERNAL_URL.value['name']: {
                    "url": url
                },
                Properties.EXTERNAL_REF.value['name']: {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                                "content": item_id
                        }
                    }]
                },
                Properties.TAGS.value['name']: {
                    "multi_select": self._expand_multi_select(post_section)
                }
            }
        )

    def save_meme(self, meme: Meme, options: Optional[dict] = None) -> None:
        self.add_gag(meme.title, meme.item_id, meme.post_web_url,
                     meme.tags, meme.cover_photo_url)

    def add_gag(self, name, item_id, url, post_section, cover_photo,
                max_retries=5, timeout=30, timeout_multiply=2):

        timeout_var = timeout
        exists_flag = False

        for _ in range(max_retries):
            try:
                exists_flag = self.exists(item_id)
                break
            except Exception:
                # TODO: Need to be written to handle specific Exceptions...
                # not sure what those expcetions are yet
                logger.warning(
                    "Error cheacking page with the following Exception\n%s",
                    traceback.format_exc()
                )
                logger.info(
                    "Waiting for %s seconds before trying again", timeout_var)
                time.sleep(timeout_var)
                timeout_var *= timeout_multiply
        else:
            raise MaxRetryError(
                f"Wasn't able to check notion page after {max_retries} tries")

        if not exists_flag:
            logger.debug("Creating page for Post ID of %s", item_id)

            timeout_var = timeout

            for _ in range(max_retries):
                try:
                    self._create_page(name, item_id, url,
                                      post_section, cover_photo)
                    break
                except Exception:
                    # TODO: Need to be written to handle specific Exceptions...
                    # not sure what those expcetions are yet
                    logger.warning(
                        "Error creating page with the following Exception\n%s",
                        traceback.format_exc()
                    )
                    logger.info(
                        "Waiting for %s seconds before trying again",
                        timeout_var)
                    time.sleep(timeout_var)
                    timeout_var *= timeout_multiply
            else:
                raise MaxRetryError(
                    f"Wasn't able to create notion page after {max_retries} "
                    "tries")


class MaxRetryError(Exception):
    """An Error raised when the app reaches the max retries amount"""
