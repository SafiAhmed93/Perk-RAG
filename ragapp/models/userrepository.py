from ragapp.models.database import Database
from azure.data.tables import TableServiceClient,UpdateMode
from ragapp.models.models import User,Role
from typing import Dict



class UserRepository:

    def __init__(self,database: Database):

        self.table_name="users"
        self.service_client=TableServiceClient.from_connection_string("UseDevelopmentStorage=true")
        self.table_client=database.get_table_client(self.table_name)

    @staticmethod
    def _entity_to_user(user_info: Dict[str, any]) -> User:

        return User(
            first_name=user_info.get("first_name"),
            last_name=user_info.get("last_name"),
            email=user_info.get("PartitionKey"),
            role=Role(user_info.get("role")).value,
            date_created=user_info.get("date_created"),
            date_last_updated=user_info.get("date_last_updated")
        )

    @staticmethod
    def _user_to_entity(user_info: User) -> Dict[str, any]:

        return {
            "PartitionKey": user_info.email,
            "RowKey": user_info.RowKey,
            "first_name": user_info.first_name,
            "last_name": user_info.last_name,
            "email": user_info.email,
            "role": user_info.role,
            "date_created": user_info.date_created,
            "date_last_updated": user_info.date_last_updated

        }
    

    def create_user(self, user_info: User) -> str | User:

        filter_expr = f"PartitionKey eq '{user_info.email}'"
        rows = self.table_client.query_entities(filter_expr)

        all_rows = [row for row in rows]

        if len(all_rows)>1:
            return f"User {user_info.email} already exists"
        
        user = self._user_to_entity(user_info)

        response = self.table_client.create_entity(user)
        
        return self._entity_to_user(response.get("content"))
    

    def get_user(self,partition_key: str, row_key: str) -> User | None:
        """
        Get the user information.
        """
     
        entity=self.table_client.get_entity(partition_key, row_key)
        
        return self._entity_to_user(entity)

    def update_user(self, partition_key: str, row_key: str, **kwargs) -> User:
        """
        Update the user information.
        
        """
       
        
        old_entity = self.table_client.get_entity(partition_key, row_key)

        # Merging the entities with new values
        new_entity = {**old_entity, **kwargs}

       
        self.table_client.update_entity(entity=new_entity,mode=UpdateMode.REPLACE)

        return self.get_user(partition_key,row_key)

        

    def delete_user(self,partition_key: str) -> str:
        filter_expr =f"PartitionKey eq '{partition_key}'"
        user_info = self.table_client.query_entities(filter_expr)

        users = [user for user in user_info]
        if len(users)>1:
            print(f"More than one entity found for partition {partition_key}")
        
        self.table_client.delete_entity(users[0].get("PartitionKey"),users[0].get("RowKey"))

        return f"User {partition_key} deleted"