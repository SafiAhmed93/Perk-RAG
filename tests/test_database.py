import pytest
from azure.data.tables import TableServiceClient
from ragapp.database import Database

test_table_name = "test"

@pytest.fixture(scope="session")
def database():
    service_client = TableServiceClient.from_connection_string("UseDevelopmentStorage=true")
    database = Database(service_client)
    yield database
    print("tear down")
    database.get_table_client(test_table_name).delete_table()

def test_setup_table(database):
    table_client = database.get_table_client(test_table_name)
    assert table_client.table_name == test_table_name
