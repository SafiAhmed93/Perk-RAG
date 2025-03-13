from .testutils import table_service_client
from ragapp.models.database import Database
import pytest
from ragapp.models.chatrepository import ChatRepository
from ragapp.models.userrepository import UserRepository
from ragapp.models.models import ChatRequest, User,Role
from datetime import datetime
import uuid


database = Database(table_service_client)
current_date=str(datetime.now())


@pytest.fixture(scope="session")
def sample_user() -> User:
    return User(first_name="m", last_name="umar", email="umar@test.com", role=Role.ADMIN.value,date_created=current_date,date_last_updated=current_date)



@pytest.fixture(scope="session")
def user_repo():
    user_repository=UserRepository(database)
    yield UserRepository(database)

    database.get_table_client(user_repository.table_name).delete_table()

def test_create_user(user_repo,sample_user):
    got = user_repo.create_user(sample_user)

    assert \
            got.first_name == sample_user.first_name and got.last_name == sample_user.last_name and got.email == sample_user.email and \
            got.role == sample_user.role and got.date_created == sample_user.date_created and got.date_last_updated == sample_user.date_last_updated
    

def test_get_user(user_repo,sample_user):
    got = user_repo.get_user(sample_user.email,sample_user.RowKey)

    assert \
            got.first_name == sample_user.first_name and got.last_name == sample_user.last_name and got.email == sample_user.email and \
            got.role == sample_user.role and got.date_created == sample_user.date_created and got.date_last_updated == sample_user.date_last_updated
    
def test_update_user(user_repo,sample_user,last_name="Umar1"):        
    got =user_repo.update_user(sample_user.email,sample_user.RowKey)

    assert \
            got.first_name == sample_user.first_name and got.last_name == sample_user.last_name and got.email == sample_user.email and \
            got.role == sample_user.role and got.date_created == sample_user.date_created and got.date_last_updated == sample_user.date_last_updated 
            




    
    