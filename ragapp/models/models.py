from dataclasses import dataclass
from typing import Optional

@dataclass
class ChatRequest:
    user: str
    message: str

@dataclass
class Response:
    status_code: int
    payload: dict