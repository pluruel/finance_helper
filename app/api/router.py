from fastapi import APIRouter

from app.api.endpoints import transaction

api_router = APIRouter()
api_router.include_router(
    transaction.router, prefix="/transaction", tags=["transaction"]
)
# api_router.include_router(items.router, prefix="/items", tags=["items"])
