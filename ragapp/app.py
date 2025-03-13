from fastapi import FastAPI

from ragapp.middleware import AuthMiddleware
from ragapp.routers.users import user_router

app = FastAPI(middleware=[
    # AuthMiddleware,
])

app.include_router(user_router)
