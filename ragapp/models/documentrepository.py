from ragapp.database import Database
from azure.data.tables import TableServiceClient, UpdateMode
from ragapp.models.models import Document, Role
from ragapp.models.abstractrepository import AbstractRepository
from typing import Dict
from ragapp.helpers.blobhelper import BlobHelper
from starlette.responses import JSONResponse

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
            "UseDevelopmentStorage=true"
        )
        self.table_client = database.get_table_client(self.table_name)
        self.blob_helper = BlobHelper()

    @staticmethod
    def _doc_to_entity(doc_info: Document) -> Dict[str, any]:
        return {
            "PartitionKey": doc_info.document_name,
            "RowKey": doc_info.document_name,
            "blob_url": doc_info.blob_url,
            "access_info": json.dumps([role.value for role in doc_info.access_info]),
            "date_created": doc_info.date_created,
            "date_last_updated": doc_info.date_last_updated,
        }

    @staticmethod
    def _entity_to_doc(doc_entity: Dict[str, any]) -> Document:

        return Document(
            document_name=doc_entity.get("PartitionKey"),
            blob_url=doc_entity.get("blob_url"),
            access_info=[
                Role(role) for role in json.loads(doc_entity.get("access_info"))
            ],
            date_created=doc_entity.get("date_created"),
            date_last_updated=doc_entity.get("date_last_updated"),
        )

    def create(self, doc_info: Document) -> Document:
        """
        Creates the document entity in the  documents table and
        uploads the document in the data lake.
        """

        self.blob_helper.upload(doc_info.document_name, doc_info.file_data)
        doc_entity = self._doc_to_entity(doc_info)
        response = self.table_client.create_entity(doc_entity)
        return self._entity_to_doc(response.get("content"))

    def get(self, partition_key: str, row_key: str) -> Document:
        """
        Gets the document information.
        """
        sas_url = self.blob_helper.get(partition_key)

        entity = self.table_client.get_entity(partition_key, row_key)
        # update the blob_url with SAS URL which will be valid for 1 hour
        entity["blob_url"] = sas_url

        return self._entity_to_doc(entity)

    def get_all(self) -> list[Document]:

        entities = [
            {**file, "blob_url": self.blob_helper.generate_sas(file["PartitionKey"])}
            for file in self.table_client.list_entities()
        ]

        return [self._entity_to_doc(entity) for entity in entities]

    def delete(self, partition_key: str, row_key: str):
        """
        Deletes the document information.

        """
        self.blob_helper.delete_blob(partition_key)
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
