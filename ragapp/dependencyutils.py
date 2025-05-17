from json import load
from ragapp.database import Database, DatabaseHelper
from ragapp.models.userrepository import UserRepository
import os
from dotenv import load_dotenv

load_dotenv()


def get_db() -> Database:
    return DatabaseHelper.get_database(os.getenv("AZURE_TABLE_CONNECTION_STRING"))


def get_user_repo():
    return UserRepository(database=get_db())
