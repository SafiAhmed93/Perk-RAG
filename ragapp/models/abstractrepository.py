from abc import ABC, abstractmethod
from typing import Dict, Any, Generic

class AbstractRepository(ABC):
    @abstractmethod
    def get(self, partition_key: str, row_key: str):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def create(self, data: Any):
        pass

    @abstractmethod
    def update(self, data: Any):
        pass

    @abstractmethod
    def delete(self, partition_key: str, row_key: str):
        pass

