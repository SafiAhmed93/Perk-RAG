from ragapp.models.models import Message, ChatRequest
from ragapp.constants import (
    llm,
    SYSTEM_MESSAGE,
    REWRITE_QUERY_SYSTEM_MESSAGE,
)
from typing import Dict


def respond(message: str, context: str, conversation: str) -> str:
    """
    Send the response to the incoming user query.

    """

    response = llm.invoke(
        f"""

        {SYSTEM_MESSAGE} \n 
        Below is the past conversation: \n{
            conversation} \n 
        below is the context retrieved \n
        {context} \n
        Below is the new user query \n
        {message}
        """
    )

    return response.content


def rewrite_query(message: Message, conversation: str):
    response = llm.invoke(
        f"""
            {REWRITE_QUERY_SYSTEM_MESSAGE} \n
            Conversation:\n
            {conversation}
            Below is the new query:\n
            {message.message}
            """
    )

    return response.content


def query_to_chat(chat: Dict) -> ChatRequest:
    """
    Convert the incoming query to a ChatRequest object.

    """

    message = Message(
        id=chat.get("message").get("id"),
        message=chat.get("message").get("message"),
        message_type=chat.get("message").get("message_type"),
        timestamp=chat.get("message").get("timestamp"),
    )

    return ChatRequest(
        user_id=chat.get("user_id"),
        message=message,
        session_id=chat.get("session_id"),
        date_created=chat.get("date_created"),
        date_last_updated=chat.get("date_last_updated"),
        conversation=chat.get("conversation"),
        response_to=chat.get("response_to"),
        Timestamp=chat.get("Timestamp"),
    )
