from typing import Any, Optional, Protocol


class Converter(Protocol):
    @classmethod
    def encode(cls, data: Any) -> dict:
        """
        Encodes the given data into a dictionary format suitable for storage
        or transmission.
        Args:
            data (Any): The data to be encoded.
        Returns:
            dict: The encoded representation of the input data.
        """
        ...

    @staticmethod
    def decode(data: dict) -> Any:
        """
        Decodes the given data dictionary into the appropriate object
        or data structure.
        Args:
            data (dict): The data to decode.
        Returns:
            Any: The decoded object or data structure.
        Raises:
            KeyError: If required keys are missing in the data.
            ValueError: If the data format is invalid.
        """
        ...


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
    @classmethod
    def encode(cls, data: str) -> dict:
        return {
            "9gag id": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": data
                    }
                }]
            }
        }

    @staticmethod
    def decode(data: dict) -> str:
        return data['properties']['9gag id']['rich_text'][0]['text']['content']


class PostTitleConverter(Converter):
    @classmethod
    def encode(cls, data: str) -> dict:
        return {
            "Name": {
                "title": [{
                    "text": {
                        "content": data
                    }
                }]
            }
        }

    @staticmethod
    def decode(data: dict) -> str:
        return data['properties']['Name']['title'][0]['text']['content']


class PostURLConverter(Converter):
    @classmethod
    def encode(cls, data: str) -> dict:
        return {'URL': {"url": data}}

    @staticmethod
    def decode(data: dict) -> Any:
        return data['properties']['URL']['url']


class PostTagsConverter(Converter, PropTypeMultiSelect):
    @classmethod
    def encode(cls, data: list) -> dict:
        return {
            "Post Section": {
                "multi_select": cls.expand_multi_select(data)
            }
        }

    @staticmethod
    def decode(data: dict) -> list:
        return [
            x['name'] for x in
            data['properties']['Post Section']['multi_select']
        ]


class PostCoverURLConverter(Converter):
    @classmethod
    def encode(cls, data: str) -> dict:
        return {
            "type": "external",
            "external": {
                    "url": data
            }
        }

    @staticmethod
    def decode(data: dict) -> str:
        return data['cover']['external']['url']


class TagsConverter(Converter, PropTypeMultiSelect):
    @classmethod
    def encode(cls, data: list) -> dict:
        return {
            "Tags": {
                "multi_select": cls.expand_multi_select(data)
            }
        }

    @staticmethod
    def decode(data: dict) -> list:
        return [
            x['name'] for x in
            data['properties']['Tags']['multi_select']
        ]


class NoteConverter(Converter):
    @classmethod
    def encode(cls, data: str) -> dict:
        return {
            "Note": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": data
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


class PageIDConverter(Converter):
    @staticmethod
    def decode(data: dict) -> str:
        return data['id']
