from json import load
from fastapi import APIRouter, Depends, File, UploadFile, Form
from pyparsing import C
from starlette.responses import JSONResponse
from ragapp.helpers.documenthelper import DocumentHelper
from ragapp.models.models import Document, Role
from typing import List
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from ragapp.models.documentrepository import DocumentRepository
from ragapp.routers import db
from ragapp.helpers.blobhelper import BlobHelper
from langchain_community.document_loaders import (
    AzureBlobStorageFileLoader,
)
from dotenv import load_dotenv
from datetime import datetime
import logging
from ragapp.constants import splitter, data_store
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


load_dotenv()

doc_repo = DocumentRepository(database=db)

doc_router = APIRouter(
    prefix="/admin/documents",
    tags=["documents"],
)
blob_helper = BlobHelper()


@doc_router.get("/")
def get_docs() -> List[Document]:
    return doc_repo.get_all()


@doc_router.get("/{document_name}", response_model=Document)
def get_doc(document_name: str):
    try:
        return doc_repo.get(document_name, document_name)
    except ResourceNotFoundError:
        return JSONResponse("User not found", 404)


@doc_router.get("/{document_name}/view")
def view_doc(document_name):
    return blob_helper.get_sas_url(document_name)


@doc_router.post("/", response_model=Document)
async def create_doc(access_info: str = Form(...), file: UploadFile = File(...)):
    if access_info is None:
        return JSONResponse("access info is missing", 400)
    try:
        blob_helper.upload(file.filename, file.file.read())
        document = Document(
            document_name=file.filename,
            access_info=[Role(int(role)) for role in access_info.split(",")],
            date_created=datetime.now(),
            date_last_updated=datetime.now(),
            indexed=False,
            processing_status="NOT STARTED",
        )
        document = doc_repo.create(document)
        process_doc(document)
        return document
    except ResourceExistsError:
        return JSONResponse("Document already exists", 409)
    except TypeError as e:
        blob_helper.delete_blob(file.filename)
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
        blob_helper.delete_blob(document_name)
        doc_repo.delete(document_name, document_name)
        return JSONResponse(f"Document - {document_name} deleted successfully", 200)
    except ResourceNotFoundError:
        return JSONResponse(f"Document - {document_name} not found", 404)


def process_doc(document: Document):
    logger.info("starting processing")
    document.processing_status = "IN PROGRESS"
    doc_repo.update(document)

    loader = AzureBlobStorageFileLoader(
        blob_helper.get_conn_string(),
        blob_helper.container_name,
        f"sample-data/{document.document_name}",
    )
    logger.info("Loader configured")

    doc_helper = DocumentHelper(splitter=splitter, loader=loader, data_store=data_store)

    done = doc_helper.process()

    if done != 0:
        logger.info("processing failed")
        document.processing_status == "FAILED"
        doc_repo.update(document)
        return

    logger.info("processing completed")
    document.processing_status = "COMPLETED"
    document.indexed = True

    logger.info("updating status")
    doc_repo.update(document)
    return "Done"
