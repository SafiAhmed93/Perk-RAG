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
from ragapp.routers import db
from ragapp.utils import query_to_chat, respond
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


@chat_router.post("/list_session")
def list_session(chat: ChatResults):

    return c.list_session(chat.user_id)


@chat_router.post("/get_chat_session")
def get_chat_session(chat: ChatResults):

    return c.get_chat_session(chat.user_id, chat.session_id)


@chat_router.post("/")
async def get_results(chat: ChatRequest) -> ChatRequest:

    if chat.context is None:
        logging.info("No context found, searching for documents")
        # Get the documents from the database
        search_results = doc_helper.query(chat.message.message)
        chat.context = doc_helper.get_context(search_results)

    print(chat.context)

    c.create_chat(chat)  # Create entity for the incoming user message

    response = respond(
        message=chat.message, context=chat.context, conversation=chat.conversation
    )  # get response for the incoming query

    logging.info(f"Response generated: {response}")

    # Create a new message object for the system response
    # with an incremented ID

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
    # Create entity for the system response
    c.create_chat(chat_request)  # Create entity for the system response.
    logging.info(f"Chat returning")

    return chat_request
