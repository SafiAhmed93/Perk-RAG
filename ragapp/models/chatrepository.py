import uuid
import os
# from database import Database
from ragapp.models.models import ChatRequest,User
from ragapp.models.database import Database

from azure.data.tables import TableServiceClient,UpdateMode
# from dotenv import load_dotenv
# from models import ChatRequest,User
from typing import List, Dict
import json
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
    def _entity_to_user(user_info: str) ->Dict[str, any]:
        
        return User(**json.loads(user_info))
    
    @staticmethod
    def _user_to_entity(user_info: User) -> User:
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

        '''
        create entity or insert rows into the chat table.
        '''

        chat = self._chat_to_entity(chat_request)

        response = self.table_client.create_entity(chat)


        return self._entity_to_chat(
            response.get("content")            
        )


    def get_chat(self, partition_key: str, row_key: str) -> ChatRequest:
        '''
        Query entity from your azure tables, 
        You can specify upto 2 filters which includes user and timestamp
        '''
        
        entity = self.table_client.get_entity(partition_key, row_key)
        
        return self._entity_to_chat(entity)


    def get_chat_history(self, partition_key: str) -> List[ChatRequest]:

        '''
        Query entities from your azure tables, 
        You can specify upto 2 filters which includes user and timestamp
        '''
        
        filter= f"PartitionKey eq '{partition_key}'"

        

        entities=self.table_client.query_entities(filter)

        for entity in entities:
            return self._entity_to_chat(entity)
        
            
             
        
    def update_chat(self,partition_key: str, row_key: str, incoming_message: str) -> str:
        '''
        Update the entities, youse partition key and Row-key
        '''
        entity=self.table_client.get_entity(partition_key,row_key)
        entity["Message"]+=incoming_message
        response = self.table_client.upsert_entity(mode=UpdateMode.REPLACE,entity=entity)
        print(response)

        return f"Done updating for partition: {partition_key} and rowkey: {row_key}"
    
    
    def delete_chat(self,partition_key: str, row_key: str) -> str:
        '''
            Deletes an entity or row from the Azure tables
        '''
        reponse = self.table_client.delete_entity(partition_key,row_key)
        print(reponse)

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
    from datetime import datetime

    service_client = TableServiceClient.from_connection_string("UseDevelopmentStorage=true")
    table_client=service_client.create_table_if_not_exists("chat")

    entity={
        "PartitionKey":"umar",
        "RowKey":"row_key3",
        "message":"message3"
    }

    filter = "PartitionKey eq 'umar'"
    entities = table_client.query_entities(filter)
    for entity in entities:
        print(entity)
    


 

   

    ...