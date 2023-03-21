from fastapi import FastAPI

from app import main
from app.core.config import settings

app = FastAPI()


app.mount(settings.API_STR, main.app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
