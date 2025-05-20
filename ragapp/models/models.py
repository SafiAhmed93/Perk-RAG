from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
import pytz


class Role(Enum):
    ADMIN = 1
    FACULTY = 2
    STUDENT = 3
    GUEST = 4


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    role: Role
    date_created: Optional[datetime] = datetime.now(pytz.timezone("Asia/Kolkata"))
    date_last_updated: Optional[datetime] = datetime.now(pytz.timezone("Asia/Kolkata"))


class Message(BaseModel):
    id: str
    message: str
    message_type: str
    timestamp: Optional[datetime] = datetime.now(pytz.timezone("Asia/Kolkata"))


class ChatRequest(BaseModel):
    user_id: str
    message: Optional[Message] = None
    session_id: Optional[str] = None
    date_created: Optional[datetime] = datetime.now(pytz.timezone("Asia/Kolkata"))
    date_last_updated: Optional[datetime] = datetime.now(pytz.timezone("Asia/Kolkata"))
    augmented_message: Optional[str] = None
    conversation: Optional[str] = None
    context: Optional[str] = None
    response_to: Optional[str] = None
    Timestamp: Optional[datetime] = None


class ChatResults(BaseModel):
    user_id: str
    session_id: Optional[str] = None


class Document(BaseModel):
    document_name: str
    access_info: List[Role]
    date_created: Optional[datetime] = datetime.now(pytz.timezone("Asia/Kolkata"))
    date_last_updated: Optional[datetime] = datetime.now(pytz.timezone("Asia/Kolkata"))
    processing_status: str
    indexed: int


class SearchResult(BaseModel):
    doc_name: str
    content: str


class Groups(BaseModel):
    name: str
    description: str
    members: List[User]


class Response(BaseModel):
    status_code: int
    payload: dict
