from abc import ABC, abstractmethod
from typing import Any, Optional


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


class PropTypeMultiSelect:
    @staticmethod
    def validate_multi_select(data: str) -> str:
        # commas create problems so the are replaced with nothing
        return data.replace(',', '')

    @classmethod
    def expand_multi_select(cls, data: list) -> list:
        """
        splits item list to object list to support creating multi selection
        on notion
        """
        return [{"name": cls.validate_multi_select(x)} for x in data]


class PostIDConverter(Converter):
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


class PostTitleConverter(Converter):
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


class PostTagsConverter(Converter, PropTypeMultiSelect):
    @classmethod
    def encode(cls, tags: list) -> dict:
        return {
            "Post Section": {
                "multi_select": cls.expand_multi_select(tags)
            }
        }

    @staticmethod
    def decode(data: dict) -> list:
        return [
            x['name'] for x in
            data['properties']['Post Section']['multi_select']
        ]


class PostCoverURLConverter(Converter):
    @staticmethod
    def encode(url: str) -> dict:
        return {
            "type": "external",
            "external": {
                    "url": url
            }
        }

    @staticmethod
    def decode(data: dict) -> str:
        return data['cover']['external']['url']


class TagsConverter(Converter, PropTypeMultiSelect):
    @classmethod
    def encode(cls, tags: list) -> dict:
        return {
            "Tags": {
                "multi_select": cls.expand_multi_select(tags)
            }
        }

    @staticmethod
    def decode(data: dict) -> list:
        return [
            x['name'] for x in
            data['properties']['Tags']['multi_select']
        ]


class NoteConverter(Converter):
    @staticmethod
    def encode(note: str) -> dict:
        return {
            "Note": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": note
                    }
                }]
            }
        }

    @staticmethod
    def decode(data: dict) -> Optional[str]:
        try:
            n = data['properties']['Note']['rich_text'][0]['text']['content']
        except IndexError:
            return None
        return n
