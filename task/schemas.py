from pydantic import BaseModel, EmailStr
from .models import TaskStatus, PriorityStatus
from datetime import datetime
from typing import Optional

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

class TeamMemberAddRequest(BaseModel):
    user_id: int
    role_id: int
class ResponseMessage(BaseModel):
    message: str
class TeamRemoveMember(BaseModel):
    user_id: int

class TaskCreate(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.NOT_STARTED
    priority: PriorityStatus = PriorityStatus.MEDIUM
    deadline: datetime
    reviewer_id: Optional[int] = None
    assignee_id: Optional[int] = None

    class Config:
        orm_mode = True
class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: PriorityStatus
    deadline: datetime
    created_at: datetime
    updated_at: datetime
    reviewer_id: Optional[int] = None
    assignee_id: Optional[int] = None
    creator_id: int
    team_id: int

    class Config:
        orm_mode = True
class TeamCreate(BaseModel):
    name: str

class TeamResponse(BaseModel):
    message: str
    team: dict
