from .testutils import table_service_client
from ragapp.models.database import Database
import pytest
from ragapp.models.chatrepository import ChatRepository
from ragapp.models.models import ChatRequest

database = Database(table_service_client)

@pytest.fixture(scope="session")
def sample_chat() -> ChatRequest:
    return ChatRequest(user = "umar", message = "test_message")

@pytest.fixture(scope="session")
def chat_repo():
    chat_repository = ChatRepository(database)
    yield ChatRepository(database)

    database.get_table_client(chat_repository.table_name).delete_table()

def test_create_chat(chat_repo, sample_chat):
    got = chat_repo.create_chat(sample_chat)

    assert got.user == sample_chat.user and got.message == sample_chat.message

def test_get_chat(chat_repo, sample_chat):
    got = chat_repo.get_chat(sample_chat.user, sample_chat.session_id)

    assert got.user == sample_chat.user and got.session_id == sample_chat.session_id


