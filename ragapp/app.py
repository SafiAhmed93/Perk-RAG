from fastapi import FastAPI
import requests
import logging
from rich.logging import RichHandler
from ragapp.middleware import AuthMiddleware, AuthorizationMiddelware
from ragapp.routers.users import user_router
from ragapp.routers.documents import doc_router
from ragapp.routers.chat import chat_router

logging.basicConfig(
    format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)]
)


app = FastAPI()

app.add_middleware(AuthorizationMiddelware)


app.include_router(user_router)

app.include_router(doc_router)

app.include_router(chat_router)
