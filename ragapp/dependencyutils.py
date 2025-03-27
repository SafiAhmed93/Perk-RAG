from ragapp.database import Database, DatabaseHelper
from ragapp.models.userrepository import UserRepository


def get_db() -> Database:
    return DatabaseHelper.get_database("UseDevelopmentStorage=true")


def get_user_repo():
    return UserRepository(database=get_db())
