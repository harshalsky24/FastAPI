from  fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from .routers import organizations, permissions, users, task, team, dashboard, websockets
from . import models
from .models import User, Task, Team
from .database import engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .database import get_db
from task.auth import get_current_user
app= FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="task/static"), name="static")

# Set up Jinja2 template directory
templates = Jinja2Templates(directory="task/templates")


origins=[
    "http://192.168.0.241:5173", 
    "http://localhost:5173/",
]
app.add_middleware(CORSMiddleware,
                   allow_origins = origins,
                   allow_credentials = True,
                   allow_methods =["*"],
                   allow_headers=["*"],
                   )
models.Base.metadata.create_all(bind=engine)

@app.get("/register/super_admin")
def register_super_admin_page(request: Request):
    return templates.TemplateResponse("register_super_admin.html",{"request": request})

@app.get("/")
def reigster_page(request: Request):
    """Render register page."""
    return templates.TemplateResponse("register.html",{"request": request})

@app.get("/organization/create")
def create_organization(request: Request):
    return templates.TemplateResponse("create_organization.html",{"request": request})

@app.get("/super_admin_login")
def super_admin_login_page(request: Request):
    return templates.TemplateResponse("super_admin_login.html",{"request": request})

@app.get("/login")
def login_page(request: Request):
    """Render login page."""
    return templates.TemplateResponse("login.html", {"request": request})

# Render Admin Permission Page
@app.get("/permissions")
def permissions_page(request: Request):
    return templates.TemplateResponse("assign_permissions.html", {"request": request})

@app.get("/admin/login")
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.get("/dashboard-ui")
def dashboard_page(request:Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/websocket-live")
def websocket_page(request:Request):
    return templates.TemplateResponse("websocket_live.html",{"request":request})

app.include_router(organizations.router)
app.include_router(users.router)
app.include_router(permissions.router)
app.include_router(team.router)
app.include_router(task.router)
app.include_router(dashboard.router)
app.include_router(websockets.router)