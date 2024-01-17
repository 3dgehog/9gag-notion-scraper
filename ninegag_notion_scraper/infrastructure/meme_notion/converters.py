from abc import ABC, abstractmethod
from typing import Any


class Converter(ABC):

    @staticmethod
    @abstractmethod
    def encode(data: Any) -> dict:
        """To send to Notion"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def decode(data: dict) -> Any:
        """To receive from Notion"""
        raise NotImplementedError


class ItemIDConverter(Converter):
    @staticmethod
    def encode(item_id: str) -> dict:
        return {
            "9gag id": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": item_id
                    }
                }]
            }
        }

    @staticmethod
    def decode(data: dict) -> str:
        return data['properties']['9gag id']['rich_text'][0]['text']['content']


class PageNameConverter(Converter):
    @staticmethod
    def encode(name: str) -> dict:
        return {
            "Name": {
                "title": [{
                    "text": {
                        "content": name
                    }
                }]
            }
        }

    @staticmethod
    def decode(data: dict) -> str:
        return data['properties']['Name']['title'][0]['text']['content']


class PostURLConverter(Converter):
    @staticmethod
    def encode(url: str) -> dict:
        return {'URL': {"url": url}}

    @staticmethod
    def decode(data: dict) -> Any:
        return data['properties']['URL']['url']


class PostTagsConverter(Converter):
    @classmethod
    def encode(cls, tags: list) -> dict:
        return {
            "Post Section": {
                "multi_select": cls._expand_multi_select(tags)
            }
        }

    @staticmethod
    def decode(data: dict) -> list:
        return data['properties']['Tags']['multi_select']

    @staticmethod
    def _validate_multi_select(data: str) -> str:
        # commas create problems so the are replaced with nothing
        return data.replace(',', '')

    @classmethod
    def _expand_multi_select(cls, data: list) -> list:
        """
        splits item list to object list to support creating multi selection
        on notion
        """
        return [{"name": cls._validate_multi_select(x)} for x in data]


class CoverURLConverter(Converter):
    @staticmethod
    def encode(url: str) -> dict:
        return {
            "type": "external",
            "external": {
                    "url": url
            }
        }

    @staticmethod
    def decode(data: dict) -> Any:
        return data['cover']['external']['url']
