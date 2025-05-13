from json import load
from azure.data.tables import TableServiceClient, TableClient
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self, service_client: TableServiceClient):
        self.service_client: TableServiceClient = service_client

    def setup_table(self, table_name: str) -> TableClient:
        try:
            table_client: TableClient = self.service_client.create_table_if_not_exists(
                table_name
            )
            print(f"Table '{table_name}' created.")
            return table_client
        except Exception:
            raise

    def get_table_client(self, table_name) -> TableClient:
        return self.setup_table(table_name)


class DatabaseHelper:
    @staticmethod
    def get_database(conn_string=os.getenv("AZURE_TABLE_CONNECTION_STRING")):
        if not conn_string:
            os.getenv("AZURE_TABLE_CONNECTION_STRING")
        table_service_client = TableServiceClient.from_connection_string(conn_string)

        db = Database(table_service_client)

        return db
