from fastapi import Request
from ragapp.routers.documents import get_doc
from ragapp.utils import query_to_chat, rewrite_query
from langchain_openai import ChatOpenAI
from openai import azure_endpoint, chat
from starlette.responses import JSONResponse
from ragapp.helpers.authentication import AuthHelper
from starlette.middleware.base import BaseHTTPMiddleware
from ragapp.helpers.documenthelper import DocumentHelper
from ragapp.constants import splitter, query_search, data_store, get_context, get_docs
from ragapp.models.documentrepository import DocumentRepository
from ragapp.models.userrepository import UserRepository
from ragapp.models.chatrepository import ChatRepository
from ragapp.models.models import ChatRequest
from dataclasses import asdict
from ragapp.routers import db
import itertools
from urllib.parse import urlencode
import json


doc_helper = DocumentHelper(splitter=splitter, data_store=data_store)
user_rep = UserRepository(db)
doc_rep = DocumentRepository(db)
chat_rep = ChatRepository(db)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        openapi_paths = ["/docs", "/openapi.json", "/"]

        if request.url.path in openapi_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return JSONResponse("Missing authentication token", 401)

        if not AuthHelper.check_valid_token(auth_header=auth_header):
            return JSONResponse("Token validation failed", 401)

        return await call_next(request)


class AuthorizationMiddelware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        openapi_paths = [
            "/docs",
            "/openapi.json",
            "/",
            "/users",
            "/documents",
            "/admin",
            "/admin/users/",
            "/admin/documents/",
            "/admin/documents/",
        ]

        if request.url.path in openapi_paths:
            return await call_next(request)

        user_query = await request.json()
        chat_object = query_to_chat(user_query)

        # Get the User and see his access
        # Get the JWT
        auth_header = request.headers.get("Authorization", None).split("Bearer")[-1]
        user = AuthHelper.get_user(auth_header)
        # user = "junaid@brio.co.in"
        print(user)

        # Get the context and document names
        search_results = query_search(
            chat_object.augmented_message or chat_object.message.message
        )

        context = get_context(search_results)
        documents = get_docs(search_results)

        doc_access = set(
            itertools.chain(*[doc_rep.get(doc, doc).access_info for doc in documents])
        )
        user_role = user_rep.get(user, user).role
        if user_role not in doc_access:
            return JSONResponse("User does not have access", 403)

        if chat_object.conversation is None:  # Meaning its a new conversation
            return await call_next(request)

        chat_object.augmented_message = rewrite_query(
            chat_object.message, chat_object.conversation
        )  # New query

        chat_object.context = context

        # Modifying the incoming object and attaching it with context
        request._body = json.dumps(asdict(chat_object)).encode()

        # print(user_role)

        print(doc_access)

        return await call_next(request)
