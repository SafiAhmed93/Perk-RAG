from ragapp.database import Database
from azure.data.tables import TableServiceClient, UpdateMode
from ragapp.models.models import Document, Role
from ragapp.models.abstractrepository import AbstractRepository
from typing import Dict
from starlette.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

# from azure.core.exceptions import (
#     ResourceExistsError,
#     ResourceModifiedError,
#     ResourceNotFoundError,
# )
import json


class DocumentRepository(AbstractRepository):
    def __init__(self, database: Database):
        self.table_name = "documents"
        self.service_client = TableServiceClient.from_connection_string(
            os.getenv("AZURE_TABLE_CONNECTION_STRING")
        )
        self.table_client = database.get_table_client(self.table_name)

    @staticmethod
    def _doc_to_entity(doc_info: Document) -> Dict[str, any]:
        return {
            "PartitionKey": doc_info.document_name,
            "RowKey": doc_info.document_name,
            "access_info": json.dumps([role.value for role in doc_info.access_info]),
            "date_created": doc_info.date_created,
            "date_last_updated": doc_info.date_last_updated,
            "indexed": doc_info.indexed,
            "processing_status": doc_info.processing_status,
        }

    @staticmethod
    def _entity_to_doc(doc_entity: Dict[str, any]) -> Document:

        return Document(
            document_name=doc_entity.get("PartitionKey"),
            access_info=[
                Role(role) for role in json.loads(doc_entity.get("access_info"))
            ],
            date_created=doc_entity.get("date_created"),
            date_last_updated=doc_entity.get("date_last_updated"),
            indexed=doc_entity.get("indexed"),
            processing_status=doc_entity.get("processing_status"),
        )

    def create(self, doc_info: Document) -> Document:
        """
        Creates the document entity in the  documents table and
        """

        response = self.table_client.create_entity(self._doc_to_entity(doc_info))
        return self._entity_to_doc(response.get("content"))

    def get(self, partition_key: str, row_key: str) -> Document:
        """
        Gets the document information.
        """

        entity = self.table_client.get_entity(partition_key, row_key)
        return self._entity_to_doc(entity)

    def get_all(self) -> list[Document]:

        docs = self.table_client.list_entities()

        return [self._entity_to_doc(doc) for doc in docs]

    def delete(self, partition_key: str, row_key: str) -> None:
        """
        Deletes the document information.

        """
        self.table_client.delete_entity(partition_key, row_key)

    def update(self, doc_info: Document) -> Document:
        """
        Update the document information.
        """

        self.table_client.update_entity(
            entity=self._doc_to_entity(doc_info), mode=UpdateMode.REPLACE
        )

        # After updating the document entity, return the updated information
        return self._entity_to_doc(
            self.table_client.get_entity(doc_info.document_name, doc_info.document_name)
        )
