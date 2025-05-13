from dotenv import load_dotenv
from fastapi import APIRouter, Depends

# from proto import Message
from ragapp.constants import llm, data_store, api_key
from ragapp.models.chatrepository import ChatRepository
from ragapp.routers import db
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

    c.create_chat(chat)
    response = c.respond(chat.message)

    message = Message(
        str(int(chat.message.id) + 1),
        response,
        "user",
        datetime.now().isoformat(),
    )

    chat_request = ChatRequest(
        chat.user,
        message,
        chat.session_id,
        datetime.now(),
        datetime.now(),
        chat.message.id,
        datetime.now(),
    )
    c.create_chat(chat_request)

    return chat_request
