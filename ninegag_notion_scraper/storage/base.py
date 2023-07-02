from abc import ABC, abstractmethod


class StorageBase(ABC):
    @abstractmethod
    def exists(self, item_id: str) -> bool: ...
