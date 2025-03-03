import uuid
import os
from ragapp.models.database import Database
from azure.data.tables import TableServiceClient,UpdateMode
# from dotenv import load_dotenv
from ragapp.models.models import ChatRequest
from typing import List, Dict
# import logging

# load_dotenv("C:\\Users\\Brio-LT-Umar\\Desktop\\PROJECTS\\GIM\\.env")

class ChatRepository:
    """
    partition_key: user email
    row_key: session id
    """
    def __init__(self,database: Database):

        self.table_name="chat"
        self.service_client=TableServiceClient.from_connection_string("UseDevelopmentStorage=true")
        self.table_client=database.get_table_client(self.table_name)
     
    @staticmethod
    def _chat_to_entity(chat_request: ChatRequest) -> Dict[str, any]:
        return {
            "PartitionKey": chat_request.user,
            "RowKey": chat_request.session_id,
            "user": chat_request.user,
            "message": chat_request.message
        }

    @staticmethod
    def _entity_to_chat(table_entity: Dict[str, any]):

        return ChatRequest(
            user=table_entity.get("user"),
            message=table_entity.get("message"),
            session_id=table_entity.get("RowKey")
        )

    def get_chat(self, partition_key: str, row_key: str) -> ChatRequest:
        '''
        Query entity from your azure tables, 
        You can specify upto 2 filters which includes user and timestamp
        '''
        
        entity = self.table_client.get_entity(partition_key, row_key)
        
        return self._entity_to_chat(entity)

    def create_chat(self, chat_request: ChatRequest) -> ChatRequest:

        '''
        create entity or insert rows into the chat table.
        '''

        chat = self._chat_to_entity(chat_request)

        response = self.table_client.create_entity(chat)


        return self._entity_to_chat(
            response.get("content")            
        )


    def get_chat_history(self, partition_key: str) -> List[ChatRequest]:

        '''
        Query entities from your azure tables, 
        You can specify upto 2 filters which includes user and timestamp
        '''
        
        filter= f"PartitionKey eq '{partition_key}'"

        records=[]
        table_client=self.client.get_table_client(os.getenv("AZ_TABLE_NAME"))

        entities=table_client.query_entities(filter)

        for entity in entities:
            records.append(ChatRequest(
                user=entity.get("PartitionKey"),
                message=entity.get("Message"),
                RowKey=entity.get("RowKey")
            ))
        return records
            
             
        
    def update_chat(self,partition_key: str, row_key: str, incoming_message: str) -> str:
        '''
        Update the entities, youse partition key and Row-key
        '''
        entity=self.table_client.get_entity(partition_key,row_key)
        entity["Message"]+=incoming_message
        self.table_client.upsert_entity(mode=UpdateMode.REPLACE,entity=entity)

        return f"Done updating for partition: {partition_key} and rowkey: {row_key}"
    
    def delete_chat(self,partition_key: str, row_key: str) -> str:
        '''
            Deletes an entity or row from the Azure tables
        '''
        self.table_client.delete_entity(partition_key,row_key)

        return f"Done Deleting for partition: {partition_key} and rowkey: {row_key}"
    

    def delete_chat_history(self,partition_key: str) -> str:

        '''
            Deletes all entities or rows for a particular partition.
        '''
        all_entites = self.list_chats(partition_key)
        
        for entity in all_entites:
            self.delete_entity(entity.user,entity.RowKey)

        return f"Deleted all entities of partiton {partition_key}"
    

 


if __name__=="__main__":
    ...