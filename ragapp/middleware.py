from fastapi import Request
from starlette.responses import JSONResponse
from ragapp.helpers.authentication import AuthHelper
from starlette.middleware.base import BaseHTTPMiddleware
from ragapp.helpers.documenthelper import DocumentHelper
from ragapp.constants import splitter, data_store
from ragapp.models.documentrepository import DocumentRepository
from ragapp.models.userrepository import UserRepository
from ragapp.routers import db
import itertools
from urllib.parse import urlencode


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

        user_query = request.query_params.get("user_query")

        # Get the JWT
        # auth_header = request.headers.get("Authorization", None).split(" ")[1]
        doc_helper = DocumentHelper(splitter=splitter, data_store=data_store)
        user_rep = UserRepository(db)
        doc_rep = DocumentRepository(db)

        raw_context = doc_helper.query(request.query_params.get("user_query"))
        context = "/n".join([content[0].page_content for content in raw_context])

        documents = list(
            {
                content[0].metadata.get("source").split("/")[-1]
                for content in raw_context
            }
        )  # Using Set to deduplicate the documents name

        # user = AuthHelper.get_user(auth_header)
        user = "junaid@brio.co.in"

        user_role = user_rep.get(user, user).role
        print(user_role)

        doc_access = set(
            itertools.chain(*[doc_rep.get(doc, doc).access_info for doc in documents])
        )
        print(doc_access)

        if user_role not in doc_access:
            return JSONResponse("User does not have access", 403)

        q_params = dict(request.query_params)
        q_params["user_query"] = f"<Context>{context}</Context> \n {user_query}"
        request.scope["query_string"] = urlencode(q_params).encode("utf-8")

        return await call_next(request)
