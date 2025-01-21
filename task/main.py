from  fastapi import FastAPI
from .routers import users, task
from . import models
from .database import engine

app= FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(users.router)
# app.include_router(task.router)
