from ast import Dict
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict

from click import Option


class Role(Enum):
    ADMIN = 1
    FACULTY = 2
    STUDENT = 3
    GUEST = 4


@dataclass
class User:
    first_name: str
    last_name: str
    email: str
    role: Role
    date_created: Optional[datetime]
    date_last_updated: Optional[datetime]


@dataclass
class Message:
    id: str
    message: str
    message_type: str
    timestamp: Optional[datetime]


@dataclass
class ChatRequest:
    user_id: str
    message: Message
    session_id: str
    date_created: Optional[datetime]
    date_last_updated: Optional[datetime]
    augmented_message: Optional[str] = None
    conversation: Optional[List[Dict]] = None
    context: Optional[str] = None
    response_to: Optional[str] = None
    Timestamp: Optional[datetime] = None


@dataclass
class Document:
    document_name: str
    access_info: List[Role]
    date_created: datetime
    date_last_updated: datetime
    processing_status: str
    indexed: int


@dataclass
class Groups:
    name: str
    description: str
    members: List[User]


@dataclass
class Response:
    status_code: int
    payload: dict
