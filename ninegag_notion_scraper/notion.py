import logging
import time
import traceback
from notion_client import Client


logger = logging.getLogger("app.notion")


class Notion:
    def __init__(self, client: Client, database_id: str) -> None:
        self._client = client
        self._db_id = database_id

    def exists(self, id):
        query = self._client.databases.query(
            database_id=self._db_id,
            filter={
                "property": "9gag id",
                "rich_text": {
                    "equals": id
                }
            })
        if len(query['results']) >= 1:
            logger.debug(f"ID {id} already exists")
            return True
        logger.debug(f"ID {id} doesn't exists")
        return False

    def _validate_multi_select(self, data: str):
        return data.replace(',', '')

    def _expand_multi_select(self, data: list):
        return [{"name": self._validate_multi_select(x)} for x in data]

    def _create_page(self, name, id, url, post_section, cover_photo):
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
                "URL": {
                    "url": url
                },
                "9gag id": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                                "content": id
                        }
                    }]
                },
                "Post Section": {
                    "multi_select": self._expand_multi_select(post_section)
                }
            }
        )

    def add_gag(self, name, id, url, post_section, cover_photo,
                max_retries=5, timeout=30, timeout_multiply=2):

        timeout_var = timeout
        exists_flag = False

        for _ in range(max_retries):
            try:
                exists_flag = self.exists(id)
                break
            except Exception:
                # TODO: Need to be written to handle specific Exceptions...
                # not sure what those expcetions are yet
                logger.warn(
                    "Error cheacking page with the following Exception\n" +
                    traceback.format_exc()
                )
                logger.info(
                    f"Waiting for {timeout_var} seconds before trying again")
                time.sleep(timeout_var)
                timeout_var *= timeout_multiply
        else:
            raise MaxRetryError(
                f"Wasn't able to check notion page after {max_retries} tries")

        if not exists_flag:
            logger.debug(f"Creating page for Post ID of {id}")

            timeout_var = timeout

            for _ in range(max_retries):
                try:
                    self._create_page(name, id, url, post_section, cover_photo)
                    break
                except Exception:
                    # TODO: Need to be written to handle specific Exceptions...
                    # not sure what those expcetions are yet
                    logger.warn(
                        "Error creating page with the following Exception\n" +
                        traceback.format_exc()
                    )
                    logger.info(
                        f"Waiting for {timeout_var} seconds before trying "
                        "again")
                    time.sleep(timeout_var)
                    timeout_var *= timeout_multiply
            else:
                raise MaxRetryError(
                    f"Wasn't able to create notion page after {max_retries} "
                    "tries")


class MaxRetryError(Exception):
    pass
