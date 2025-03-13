from ragapp.models.database import Database
from azure.data.tables import TableServiceClient,UpdateMode
from ragapp.models.models import Document,Role
from typing import Dict
import json

class DocumentRepository:
    def __init__(self,database: Database):
        self.table_name="documents"
        self.service_client = TableServiceClient.from_connection_string("UseDevelopmentStorage=true")
        self.table_client = database.get_table_client(self.table_name)

    @staticmethod
    def _doc_to_entity(doc_info: Document) -> Dict[str, any]:
        return {
            "PartitionKey": doc_info.document_name,
            "RowKey": doc_info.document_name,
            "blob_url":doc_info.blob_url,
            "access_info": json.dumps([role.value for role in doc_info.access_info]),
            "date_created": doc_info.date_created,
            "date_last_updated": doc_info.date_last_updated

        }

    @staticmethod
    def _entity_to_doc(doc_entity: Dict[str, any]) -> Document:

        return Document(
            document_name=doc_entity.get("PartitionKey"),
            blob_url=doc_entity.get("blob_url"),
            access_info=[Role(role) for role in json.loads(doc_entity.get("access_info"))],
            date_created=doc_entity.get("date_created"),
            date_last_updated=doc_entity.get("date_last_updated")


        )

    def create_doc(self, doc_info: Document) -> Document:

        """
        Creates the document entity in the  documents table.
        """

        doc_entity=self._doc_to_entity(doc_info)

        response = self.table_client.create_entity(doc_entity)

        return self._entity_to_doc(response.get("content"))
    
    def get_doc(self, partition_key: str, row_key: str) -> Document:
        """
        Gets the document information.
        """
        entity=self.table_client.get_entity(partition_key, row_key)

        return self._entity_to_doc(entity)
    
    def delete_doc(self,partition_key: str, row_key: str):
        """
        Deletes the document information.
        """
        self.table_client.delete_entity(partition_key, row_key)

    def update_doc(self, partition_key: str, row_key: str, **kwargs) -> Document:
        """
        Update the document information.
        """
        old_entity=self.table_client.get_entity(partition_key, row_key)

        new_entity = {**old_entity, **kwargs}

        self.table_client.update_entity(entity=new_entity, mode=UpdateMode.REPLACE)

        return self.get_doc(partition_key, row_key)

        



