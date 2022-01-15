import os
import logging
import time
import traceback
from notion_client import Client

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DATABASE = os.environ["NOTION_DATABASE"]

logger = logging.getLogger("app.notion")

client = Client(auth=NOTION_TOKEN)


def exists(id):
    query = client.databases.query(
        database_id=NOTION_DATABASE,
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


def _validate_multi_select(data: str):
    return data.replace(',', '')


def _create_page(name, id, url, post_section, cover_photo):
    client.pages.create(
        parent={"database_id": NOTION_DATABASE},
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
                "multi_select": [{
                    "name": _validate_multi_select(post_section)
                }]
            }
        }
    )


def add_gag(name, id, url, post_section, cover_photo,
            max_retries=5, timeout=30, timeout_multiply=2):

    timeout_var = timeout
    exists_flag = False

    for _ in range(max_retries):
        try:
            exists_flag = exists(id)
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
                _create_page(name, id, url, post_section, cover_photo)
                break
            except Exception:
                # TODO: Need to be written to handle specific Exceptions...
                # not sure what those expcetions are yet
                logger.warn(
                    "Error creating page with the following Exception\n" +
                    traceback.format_exc()
                )
                logger.info(
                    f"Waiting for {timeout_var} seconds before trying again")
                time.sleep(timeout_var)
                timeout_var *= timeout_multiply
        else:
            raise MaxRetryError(
                f"Wasn't able to create notion page after {max_retries} tries")


class MaxRetryError(Exception):
    pass
