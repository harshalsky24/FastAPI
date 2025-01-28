from pydantic import BaseModel, EmailStr
from .models import TaskStatus, PriorityStatus
from datetime import datetime
from typing import Optional, List
from pydantic import constr

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

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
    status: TaskStatus
    priority: PriorityStatus 
    deadline: datetime
    reviewer_id: Optional[int] = None
    assignee_id: Optional[int] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    deadline: Optional[datetime]  # Allow None values
    creator_id: int
    team_id: int
    reviewer_id: Optional[int]  # Allow None values
    assignee_id: Optional[int]

class TeamCreate(BaseModel):
    name: str

class TeamResponse(BaseModel):
    message: str
    team: dict

    class Config:
        from_attributes = True

class TaskUpdateRequest(BaseModel):
    task_id: int
    description: Optional[str] = None
    priority: PriorityStatus
    assignee_id: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    assignee_id: Optional[int]
    creator_id: int
    team_id: int

class DeleteTaskRequest(BaseModel):
    task_id: int

################### USER-DASHBOAORD-SCHEMAS #########
# class UserTaskResponse(BaseModel):
#     id: int
#     title: str
#     status: str
#     priority: str
#     deadline: datetime

# class UserDashboardResponse(BaseModel):
#     user_id: int
#     username: str
#     assigned_tasks: List[UserTaskResponse]
#     created_tasks: List[UserTaskResponse]
#     review_tasks: List[UserTaskResponse]

class TokenData(BaseModel):
    email: str | None = None

class TaskResponseSchema(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    deadline: datetime
    created_at: datetime
    assignee_id: int

    class Config:
        from_attributes = True 
    
class RoleCreateRequest(BaseModel):
    role_name: str