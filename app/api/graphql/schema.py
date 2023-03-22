import strawberry
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter

from app.api.deps import get_db
from app.models import Item


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, world!"


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_item(self, db: Session = Depends(get_db)) -> str:
        with db.begin():
            item = Item()

        return "Hello, world!"


schema = strawberry.Schema(query=Query, mutation=Mutation)
