from fastapi import FastAPI

from app import main
from app.core.config import settings

app = FastAPI()


app.mount(settings.API_STR, main.app)
