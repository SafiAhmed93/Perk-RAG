import os
from dotenv import load_dotenv
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeDirectoryClient,
    FileSystemClient,
    FileSasPermissions,
    UserDelegationKey,
    generate_file_sas,
)
from azure.mgmt.storage import StorageManagementClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError
from typing import Dict, Any
from datetime import datetime, timedelta
from pytz import timezone
import base64

load_dotenv(".env")


class BlobHelper:

    def __init__(self):
        self.account_name = os.getenv("AZURE_DATALAKE_ACCOUNT_NAME")
        self.account_url = f"https://{self.account_name}.dfs.core.windows.net"
        self.container_name = os.getenv("AZURE_DATALAKE_CONTAINER_NAME")
        self.directory_name = os.getenv("AZURE_DATALAKE_DATA_DIRECTORY")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.credential = DefaultAzureCredential()
        self.datalake_service_client = DataLakeServiceClient(
            self.account_url, credential=self.credential
        )
        self.filesystem_client = FileSystemClient(
            self.account_url, self.container_name, credential=self.credential
        )
        self.directory_client = DataLakeDirectoryClient(
            account_url=self.account_url,
            file_system_name=self.container_name,
            directory_name=self.directory_name,
            credential=self.credential,
        )
        self.storage_management_client = StorageManagementClient(
            self.credential, self.subscription_id
        )

    def get_user_delegation_key(self) -> UserDelegationKey:
        user_delegation_key = self.datalake_service_client.get_user_delegation_key(
            datetime.now(timezone("UTC")),
            datetime.now(timezone("UTC")) + timedelta(hours=1),
        )

        return user_delegation_key

    def get_sas_token(self, file_name: str):

        return generate_file_sas(
            account_name=self.directory_client.account_name,
            file_system_name=self.directory_client.file_system_name,
            directory_name=self.directory_name,
            file_name=file_name,
            permission=FileSasPermissions(read=True),
            expiry=datetime.now(timezone("UTC")) + timedelta(hours=1),
            credential=self.get_user_delegation_key(),
        )

    def get_sas_url(self, file_name: str):

        sas_token = self.get_sas_token(file_name)
        return f'{os.getenv("AZURE_BLOB_URL")}/{file_name}?{sas_token}'

    def upload(self, file_name: str, file_data: bytes) -> Dict[str, Any]:

        file_client = self.directory_client.get_file_client(file_name)

        return file_client.upload_data(file_data, overwrite=True)

    def list(self):
        try:

            files = self.filesystem_client.get_paths(self.directory_name)
            return [file.split("/")[-1] for file in files]

        except ResourceNotFoundError:

            return "File name specified does not exist"

    def get(self, file_name: str):

        # First we will  create the SAS token for the file, which will have an expiry of one hour.
        sas_token = self.get_sas_token(file_name)
        # Create the SAS URl
        return f'{os.getenv("AZURE_BLOB_URL")}/{file_name}?{sas_token}'

    def delete_blob(self, file_name: str) -> None:
        try:
            file_client = self.directory_client.get_file_client(file_name)
            return file_client.delete_file()
        except ResourceNotFoundError:
            return "File resource does not exist"

    def get_file_bytes(self, file_name: str) -> bytes:
        file_client = self.directory_client.get_file_client(file_name)
        file_client.download_file().readall()

    def get_conn_string(self):
        keys = self.storage_management_client.storage_accounts.list_keys(
            self.resource_group, self.account_name
        ).keys
        key = [key.value for key in keys][0]
        return f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={key};EndpointSuffix=core.windows.net"
