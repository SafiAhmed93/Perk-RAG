from ragapp.models.models import ChatRequest,User
from ragapp.models.database import Database
from azure.data.tables import TableServiceClient,UpdateMode
from typing import List, Dict
import json


class ChatRepository:
    """
    partition_key: user email
    row_key: session id
    """
    def __init__(self, database: Database):

        self.table_name="chat"
        self.service_client=TableServiceClient.from_connection_string("UseDevelopmentStorage=true")
        self.table_client=database.get_table_client(self.table_name)

    @staticmethod
    def _entity_to_user(user_info: str) -> User:
        
        return User(**json.loads(user_info))
    
    @staticmethod
    def _user_to_entity(user_info: User) -> str:
        return json.dumps(user_info.__dict__)
     
    @staticmethod
    def _chat_to_entity(chat_request: ChatRequest) -> Dict[str, any]:

        return {
            "PartitionKey": chat_request.user.email,
            "RowKey": chat_request.session_id,
            "user": ChatRepository._user_to_entity(chat_request.user),
            "message": chat_request.message,
            "date_created": chat_request.date_created,
            "date_last_updated": chat_request.date_last_updated
        }

    @staticmethod
    def _entity_to_chat(table_entity: Dict[str, any]) -> ChatRequest:

        return ChatRequest(
            user=ChatRepository._entity_to_user(table_entity.get("user")),
            message=table_entity.get("message"),
            session_id=table_entity.get("RowKey"),
            date_created = table_entity.get("date_created"),
            date_last_updated = table_entity.get("date_last_updated")
        )
    

    def create_chat(self, chat_request: ChatRequest) -> ChatRequest:

        """
        create entity or insert rows into the chat table.
        """

        chat = self._chat_to_entity(chat_request)

        response = self.table_client.create_entity(chat)


        return self._entity_to_chat(
            response.get("content")            
        )


    def get_chat(self, partition_key: str, row_key: str) -> ChatRequest:
        """
        Query entity from your azure tables,
        You can specify upto 2 filters which includes user and timestamp
        """
        
        entity = self.table_client.get_entity(partition_key, row_key)
        
        return self._entity_to_chat(entity)


    def get_chat_history(self, partition_key: str) -> List[ChatRequest]:

        """
        Query entities from your azure tables,
        You can specify upto 2 filters which includes user and timestamp
        """
        
        filter_expression= f"PartitionKey eq '{partition_key}'"

        entities=self.table_client.query_entities(filter_expression)


        return [self._entity_to_chat(entity) for entity in entities]
            
             
        
    def update_chat(self,partition_key: str, row_key: str, incoming_message: str) -> str:
        """
        Update the chat information
        """
        entity=self.table_client.get_entity(partition_key,row_key)
        entity["Message"]+=incoming_message
        self.table_client.upsert_entity(mode=UpdateMode.REPLACE,entity=entity)
        
        return f"Done updating for partition: {partition_key} and row_key: {row_key}"
    
    
    def delete_chat(self,partition_key: str, row_key: str) -> str:
        """
            Deletes an entity or row from the Azure tables
        """
        self.table_client.delete_entity(partition_key,row_key)
        

        return f"Done Deleting for partition: {partition_key} and row_key: {row_key}"
    

    def delete_chat_history(self,partition_key: str) -> str:

        """
            Deletes all entities or rows for a particular partition.
        """
        all_entities = self.get_chat_history(partition_key)
        
        for entity in all_entities:
            self.delete_chat(entity.user.email,entity.session_id)

        return f"Deleted all entities of partition {partition_key}"
    