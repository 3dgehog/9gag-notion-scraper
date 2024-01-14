from enum import Enum
from notion_client import Client


class Properties(Enum):
    EXTERNAL_REF = {"name": "9gag id", "type": "rich_text"}
    EXTERNAL_URL = {"name": "URL", "type": "url"}
    TAGS = {"name": "Post Section", "type": "multi_select"}


class NotionBase:
    def __init__(self, client: Client, database_id: str) -> None:
        self._client = client
        self._db_id = database_id
        self._validate_database_schema(database_id)

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
