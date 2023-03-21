from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from strawberry.fastapi import GraphQLRouter

from app.core.config import settings
from app.graphql.schema import schema

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


router = GraphQLRouter(schema=schema)

app.include_router(router, prefix="/graphql")
