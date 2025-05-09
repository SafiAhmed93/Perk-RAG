from ragapp.database import DatabaseHelper
import os

db = DatabaseHelper.get_database(os.getenv("AZURE_TABLE_CONNECTION_STRING"))
