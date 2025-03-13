from .testutils import table_service_client
from ragapp.database import Database
import pytest
from ragapp.models.chatrepository import ChatRepository
from ragapp.models.models import ChatRequest, User
from datetime import datetime

database = Database(table_service_client)
current_date=str(datetime.now())


@pytest.fixture(scope="session")
def sample_chat() -> ChatRequest:
    user = User(first_name="umar", last_name="..", email="umar@test.com", role="Data Engineer",date_created=current_date,date_last_updated=current_date)
    return ChatRequest(user = user, message = "test_message",date_created=current_date,date_last_updated=current_date)



@pytest.fixture(scope="session")
def chat_repo():
    chat_repository = ChatRepository(database)
    yield ChatRepository(database)

    database.get_table_client(chat_repository.table_name).delete_table()


# @pytest.mark.dependency(name="create_chat")
def test_create_chat(chat_repo, sample_chat):
    got = chat_repo.create_chat(sample_chat)

    assert \
            got.user == sample_chat.user and got.message == sample_chat.message and got.date_created == sample_chat.date_created and \
            got.date_last_updated == sample_chat.date_last_updated

# @pytest.mark.dependency(name="get_chat", depends=["create_chat"])
def test_get_chat(chat_repo, sample_chat):
    got = chat_repo.get_chat(sample_chat.user.email, sample_chat.session_id)

    assert \
             got.user == sample_chat.user and got.message == sample_chat.message and got.date_created == sample_chat.date_created and \
             got.date_last_updated == sample_chat.date_last_updated
    

# @pytest.mark.dependency(name="get_chat_history",depends=["get_chat"])
def test_get_chat_history(chat_repo,sample_chat):

    gots = chat_repo.get_chat_history(sample_chat.user.email)

    for got in gots:

        assert \
            got.user == sample_chat.user and got.message == sample_chat.message and got.date_created == sample_chat.date_created and \
            got.date_last_updated == sample_chat.date_last_updated
            



