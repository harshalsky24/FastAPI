from pydantic import BaseModel, EmailStr
from .models import TaskStatus, Priority
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TaskBase(BaseModel):
    title: str
    description: str
    priority: Priority
    deadline: datetime

class TaskCreate(TaskBase):
    assignee_id: int
    reviewer_id: int

class TaskOut(TaskBase):
    id: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
