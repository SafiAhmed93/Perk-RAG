from datetime import datetime
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

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
    RowKey: Optional[str]="12345"

@dataclass
class ChatRequest:
    user: User
    date_created: datetime
    date_last_updated: datetime
    session_id: Optional[str]=str(uuid.uuid4())
    message: Optional[str]=None
    Timestamp: Optional[datetime]=None

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
