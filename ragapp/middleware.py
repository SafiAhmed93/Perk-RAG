from fastapi import Request
from starlette.responses import  JSONResponse
from ragapp.helpers.authentication import AuthHelper
from starlette.middleware.base import BaseHTTPMiddleware

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