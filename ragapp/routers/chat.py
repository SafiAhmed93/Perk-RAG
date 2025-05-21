import itertools
import time
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request

# from proto import Message
from ragapp.constants import (
    llm,
    data_store,
    splitter,
    api_key,
    query_search,
)
from ragapp.models.chatrepository import ChatRepository
from ragapp.models.documentrepository import DocumentRepository
from ragapp.models.userrepository import UserRepository
from ragapp.routers import db, documents
from ragapp.utils import query_to_chat, respond, rewrite_query
from ragapp.helpers.documenthelper import DocumentHelper
from ragapp.models.models import ChatRequest, Message, ChatResults
from datetime import datetime
import logging


load_dotenv()


chat_router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

c = ChatRepository(database=db)
doc_helper = DocumentHelper(splitter=splitter, data_store=data_store)
doc_rep = DocumentRepository(db)
user_rep = UserRepository(db)


@chat_router.post("/list_session")
def list_session(chat: ChatResults):

    return c.list_session(chat.user_id)


@chat_router.post("/get_chat_session")
def get_chat_session(chat: ChatResults):

    return c.get_chat_session(chat.user_id, chat.session_id)


@chat_router.post("/")
async def get_results(chat: ChatRequest) -> ChatRequest:

    search_results = None
    response = None
    c.create_chat(chat)
    query = None
    message = None

    if chat.conversation == "[]":
        query = chat.message.message  # get response for the incoming query
    else:
        chat.augmented_message = rewrite_query(chat.message, chat.conversation)
        query = chat.augmented_message

    search_results = doc_helper.query(query)
    documents = doc_helper.get_docs(search_results)
    doc_access = set(
        itertools.chain(*[doc_rep.get(doc, doc).access_info for doc in documents])
    )
    user_role = user_rep.get(chat.user_id, chat.user_id).role

    chat.context = doc_helper.get_context(search_results)

    if user_role not in doc_access:
        message = Message(
            id=str(int(chat.message.id) + 1),
            message="Sorry you do not have access to the document containing this information.",
            message_type="system",
            timestamp=datetime.now().isoformat(),
        )
    else:
        response = respond(
            message=query,
            context=chat.context,
            conversation=chat.conversation,
        )

        message = Message(
            id=str(int(chat.message.id) + 1),
            message=response,
            message_type="system",
            timestamp=datetime.now().isoformat(),
        )

    chat_request = ChatRequest(
        user_id=chat.user_id,
        message=message,
        session_id=chat.session_id,
        date_created=datetime.now(),
        date_last_updated=datetime.now(),
        response_to=chat.message.id,
        Timestamp=datetime.now(),
    )
    logging.info(f"Chat generated and now writing to the database")
    c.create_chat(chat_request)
    logging.info(f"Chat returning")

    return chat_request
