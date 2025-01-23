from  fastapi import FastAPI
from .routers import users, task, team, dashboard
from . import models
from .database import engine

app= FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(team.router)
app.include_router(task.router)
app.include_router(dashboard.router)