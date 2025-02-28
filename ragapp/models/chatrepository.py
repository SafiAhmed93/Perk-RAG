import uuid

from azure.data.tables import TableServiceClient

from ragapp.models.models import ChatRequest
from typing import List, Dict


class ChatRepository:
    def __init__(self):
        self.client = TableServiceClient.from_connection_string("").get_table_client("chat")

    @staticmethod
    def _chat_to_entity(partition_key: str, row_key: str, chat_request: ChatRequest) -> Dict[str, any]:
        return {
            "PartitionKey": partition_key,
            "RowKey": row_key,
            "user": chat_request.user,
            "message": chat_request.message
        }

    @staticmethod
    def _entity_to_chat(table_entity: Dict[str, any]):
        return ChatRequest(
            user=table_entity.get("user"),
            message=table_entity.get("message")
        )

    def get_chat(self, partition_key: str, row_key: str) -> ChatRequest:
        return self._entity_to_chat(self.client.get_entity(
            partition_key,
            row_key
        ))

    def list_chat(self, partition_key: str) -> List[str]:

        return self.client.query_entities(
            partition_key
        )

    def create_chat(self, chat_request: ChatRequest) -> str:
        self.client.create_entity(
            self._chat_to_entity(chat_request.user, str(uuid.uuid4()), chat_request)
        )
        return "done"

    # def get_all_chats(self):
    #     return self.client.list_entities()