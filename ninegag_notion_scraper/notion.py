import os
import logging
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
    return False


def _validate_multi_select(data: str):
    return data.replace(',', '')


def add_gag(name, id, url, post_section, cover_photo):
    if not exists(id):
        logger.debug(f"Creating page for Post ID of {id}")
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
