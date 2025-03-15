from fastapi import APIRouter
from starlette.responses import JSONResponse
from ragapp.models.models import Document
from typing import List
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from ragapp.models.documentrepository import DocumentRepository
from ragapp.routers import db
from ragapp.helpers.blobhelper import BlobHelper

doc_repo = DocumentRepository(database=db)

doc_router = APIRouter(
    prefix="/admin/documents",
    tags=["documents"],
)
helper = BlobHelper()


@doc_router.get("/")
def get_docs() -> List[Document]:
    return doc_repo.get_all()


@doc_router.get("/{document_name}", response_model=Document)
def get_doc(document_name: str):
    try:
        return doc_repo.get(document_name, document_name)
    except ResourceNotFoundError:
        return JSONResponse("User not found", 404)


@doc_router.post("/", response_model=Document)
def create_doc(document: Document):

    if document.file_data is None:
        return JSONResponse("File data is of None type", 500)

    try:
        document = doc_repo.create(document)
        return document
    except ResourceExistsError:
        return JSONResponse("Document already exists", 409)
    except TypeError as e:
        doc_repo.delete(document.document_name, document.document_name)
        return JSONResponse(repr(e), 500)


@doc_router.put("/{document_name}", response_model=Document)
def update_doc(document_name: str, document: Document):
    try:
        if document.document_name != document_name:
            return JSONResponse("Bad request, document name doesn't match", 400)
        return doc_repo.update(document)
    except ResourceNotFoundError:
        return JSONResponse(f"document - {document_name} not found", 404)
    except Exception as e:
        return repr(e)


@doc_router.delete("/{document_name}")
def delete_doc(document_name: str):
    try:
        helper.delete_blob(document_name)
        doc_repo.delete(document_name, document_name)
        return JSONResponse(f"Document - {document_name} deleted successfully", 200)
    except ResourceNotFoundError:
        return JSONResponse(f"Document - {document_name} not found", 404)
