from fastapi import APIRouter
from starlette.responses import JSONResponse
from ragapp.models.models import User
from typing import List, Union
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from ragapp.models.userrepository import UserRepository
from ragapp.routers import db


user_repo = UserRepository(database=db)

user_router = APIRouter(
    prefix="/admin/users",
    tags=["users"],
)


@user_router.get("/")
def get_users() -> List[User]:
    return user_repo.get_all()


@user_router.get("/{user_id}", response_model=User)
def get_user(user_id: str):
    try:
        return user_repo.get(user_id, user_id)
    except ResourceNotFoundError:
        return JSONResponse("User not found", 404)


@user_router.post("/", response_model=User)
def create_user(user: User):
    try:
        user = user_repo.create(user)
        return user
    except ResourceExistsError:
        return JSONResponse("User already exists", 409)
    except TypeError as e:
        user_repo.delete(user.email, user.email)
        return JSONResponse(repr(e), 500)


@user_router.put("/{user_id}", response_model=User)
def update_user(user_id: str, user: User):
    try:
        if user.email != user_id:
            return JSONResponse("Bad request, user_id doesn't match", 400)
        return user_repo.update(user)
    except ResourceNotFoundError:
        return JSONResponse(f"User - {user_id} not found", 404)


@user_router.delete("/{user_id}")
def delete_user(user_id: str):
    try:
        user_repo.delete(user_id, user_id)
        return JSONResponse(f"User - {user_id} deleted successfully", 200)
    except ResourceNotFoundError:
        return JSONResponse(f"User - {user_id} not found", 404)
