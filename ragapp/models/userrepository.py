from ragapp.database import Database
from azure.data.tables import TableServiceClient,UpdateMode

from ragapp.models.abstractrepository import AbstractRepository
from ragapp.models.models import User,Role
from typing import Dict, List

class UserRepository(AbstractRepository):

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
            role=Role(user_info.get("role")),
            date_created=user_info.get("date_created"),
            date_last_updated=user_info.get("date_last_updated")
        )

    @staticmethod
    def _user_to_entity(user_info: User) -> Dict[str, any]:
        return {
            "PartitionKey": user_info.email,
            "RowKey": user_info.email,
            "first_name": user_info.first_name,
            "last_name": user_info.last_name,
            "email": user_info.email,
            "role": user_info.role.value,
            "date_created": user_info.date_created,
            "date_last_updated": user_info.date_last_updated

        }

    def create(self, user_info: User) -> str | User:
        response = self.table_client.create_entity(
            self._user_to_entity(user_info)
        )
        return self._entity_to_user(response.get("content"))

    def get(self,partition_key: str, row_key: str) -> User | None:
        """
        Get the user information.
        """
     
        entity=self.table_client.get_entity(partition_key, row_key)
        
        return self._entity_to_user(entity)

    def get_all(self) -> List[User] | None:
        """
        Get the user information.
        """

        users = self.table_client.list_entities()

        return [self._entity_to_user(user) for user in users]

    def update(self, user: User )-> User:
        """
        Update the user information.
        
        """
        self.table_client.update_entity(
            entity=self._user_to_entity(user),
            mode=UpdateMode.REPLACE
        )

        return self.get(user.email,user.email)

    def delete(self, partition_key: str, row_key: str) -> str:

        self.table_client.delete_entity(partition_key, row_key)

        return f"User {partition_key} deleted"