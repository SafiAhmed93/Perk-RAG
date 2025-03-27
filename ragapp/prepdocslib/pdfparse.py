from langchain_community.document_loaders import (
    AzureBlobStorageFileLoader,
)
from langchain_core.documents import Document as langchain_document
from azure.identity import DefaultAzureCredential

# from ragapp.helpers.blobhelper import BlobHelper
from blobhelper2 import BlobHelper
from dotenv import load_dotenv
from typing import List, Dict
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()


class PdfParse:
    def __init__(self):
        self.blob_helper = BlobHelper()

    def get_page_content(self, file_name) -> List[langchain_document]:

        loader = AzureBlobStorageFileLoader(
            self.blob_helper.get_conn_string(),
            self.blob_helper.container_name,
            f"sample-data/{file_name}",
        )

        logger.info("Document successfully loaded")
        return loader.load()
