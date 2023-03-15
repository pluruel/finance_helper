from fastapi import APIRouter

from app.api.api_v1.endpoints import login, users, files

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["user"])
api_router.include_router(files.router, prefix="/files", tags=["utils"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])
