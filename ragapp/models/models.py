import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List

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
    date_created: datetime
    date_last_updated: datetime

@dataclass
class ChatRequest:
    user: User
    message: str
    date_created: datetime
    date_last_updated: datetime

@dataclass
class Document:
    document_name: str
    blob_url: str
    access_info: List[Role]
    date_created: datetime
    date_last_updated: datetime

@dataclass
class Group:
    name: str
    description: str
    members: List[User]

@dataclass
class Response:
    status_code: int
    payload: dict