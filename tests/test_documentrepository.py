from .testutils import table_service_client
from ragapp.models.database import Database
import pytest
from ragapp.models.documentrepository import DocumentRepository
from ragapp.models.models import User,Role,Document
from datetime import datetime
import json

database = Database(table_service_client)
current_date=str(datetime.now())

@pytest.fixture(scope="session")
def sample_doc() -> Document:
    return Document(document_name="test_doc",blob_url="https://testdoc.com",access_info=[Role(1),Role(2)],
                    date_created=current_date,date_last_updated=current_date)

@pytest.fixture(scope="session")
def doc_repo():
    doc_repository=DocumentRepository(database)
    yield DocumentRepository(database)

    database.get_table_client(doc_repository.table_name).delete_table()


def test_create_doc(doc_repo,sample_doc):
    got = doc_repo.create_doc(sample_doc)

    assert got.document_name == sample_doc.document_name

def test_get_doc(doc_repo,sample_doc):
    got = doc_repo.get_doc(sample_doc.document_name,sample_doc.document_name)

    assert got.document_name == sample_doc.document_name and got.access_info == sample_doc.access_info

def test_update_doc(doc_repo,sample_doc):

    got = doc_repo.update_doc(sample_doc.document_name,sample_doc.document_name)

    assert got.document_name == sample_doc.document_name and got.access_info == sample_doc.access_info

