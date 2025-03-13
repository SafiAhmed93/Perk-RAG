from fastapi import FastAPI, Depends, Header, Request, HTTPException
from typing import Annotated, Dict
from ragapp.models.models import ChatRequest
from ragapp.helpers.authentication import AuthHelper
from starlette.responses import JSONResponse


app = FastAPI()


@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    openapi_paths = ["/docs", "/redoc", "/openapi.json", "/"]

    if request.url.path in openapi_paths:
        return await call_next(request)

    auth_header = request.headers.get("Authorization", None)
    if not auth_header:
        return JSONResponse("Missing authentication token", 401)

    if not AuthHelper.check_valid_token(auth_header=auth_header):
        return JSONResponse("Token validation failed", 401)

    return await call_next(request)


@app.get("/protected")
async def read_root():
    return {"message": "You have access"}
