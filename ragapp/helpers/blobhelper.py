import os
from dotenv import load_dotenv
from azure.storage.filedatalake import (
    DataLakeDirectoryClient,
    FileSystemClient,
    generate_file_sas,
    FileSasPermissions,
)
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from typing import Dict, Any
from datetime import datetime, timedelta
import base64

load_dotenv(".env")


class BlobHelper:

    def __init__(self):
        self.account_name = os.getenv("AZURE_DATALAKE_ACCOUNT_NAME")
        self.account_url = f"https://{self.account_name}.dfs.core.windows.net"
        self.container_name = os.getenv("AZURE_DATALAKE_CONTAINER_NAME")
        self.directory_name = os.getenv("AZURE_DATALAKE_DATA_DIRECTORY")
        self.credential = os.getenv("AZURE_DATALAKE_SAS_TOKEN")
        self.filesystem_client = FileSystemClient(
            self.account_url,
            self.container_name,
            credential=self.credential
        )
        self.directory_client = DataLakeDirectoryClient(
            account_url=self.account_url,
            file_system_name=self.container_name,
            directory_name=self.directory_name,
            credential = self.credential,
        )

    
    def generate_sas(self, file_name: str):

        sas_token = generate_file_sas(
            account_name=self.account_name,
            file_system_name=self.container_name,
            directory_name=self.directory_name,
            file_name=file_name,
            credential=self.credential,
            permission=FileSasPermissions(read=True),
            expiry=datetime.now() + timedelta(hours=1)
        )

        return f"{os.getenv("AZURE_BLOB_URL")}/{file_name}?{sas_token}"


    def upload(self, file_name: str, file_data: str) -> Dict[str, Any]:

        file_data=base64.b64decode(file_data)
        file_client = self.directory_client.get_file_client(file_name)

        return file_client.upload_data(file_data,overwrite=True)

    def list(self):
        try:

            files = self.filesystem_client.get_paths(self.directory_name)
            return [file.get("name").split("/")[-1] for file in files]

        except ResourceNotFoundError:

            return "File name specified does not exist"

    def get(self, file_name: str):

        # First we will  create the SAS token for the file, which will have an expiry of one hour.
        sas_token = self.generate_sas(file_name)
        # Create the SAS URl
        return f"{os.getenv("AZURE_BLOB_URL")}/{file_name}?{sas_token}"

        

    def delete_blob(self, file_name: str) -> None:
        try:
            file_client = self.directory_client.get_file_client(file_name)
            return file_client.delete_file()
        except ResourceNotFoundError:
            return "File resource does not exist"