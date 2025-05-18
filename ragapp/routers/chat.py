import time
from dotenv import load_dotenv
from fastapi import APIRouter, Depends

# from proto import Message
from ragapp.constants import (
    llm,
    data_store,
    api_key,
    query_search,
    get_context,
    get_docs,
)
from ragapp.models.chatrepository import ChatRepository
from ragapp.routers import db
from ragapp.utils import query_to_chat, respond
from ragapp.models.models import ChatRequest, Message
from datetime import datetime


load_dotenv()


chat_router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

c = ChatRepository(database=db)


@chat_router.get("/")
def get_chat():
    return "chat"


@chat_router.post("/")
async def get_results(chat: ChatRequest) -> ChatRequest:

    if chat.context is None:
        search_results = query_search(chat.message.message)
        chat.context = get_context(search_results)

    print(chat.context)

    c.create_chat(chat)  # Create entity for the incoming user message

    response = respond(
        message=chat.message, context=chat.context, conversation=chat.conversation
    )  # get response for the incoming query

    print(response)

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
    c.create_chat(chat_request)  # Create entity for the system response.

    return chat_request
