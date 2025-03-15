from fastapi import FastAPI

from ragapp.middleware import AuthMiddleware
from ragapp.routers.users import user_router
from ragapp.routers.documents import doc_router

app = FastAPI(
    middleware=[
        # AuthMiddleware,
    ]
)

# app.include_router(user_router)

app.include_router(doc_router)
