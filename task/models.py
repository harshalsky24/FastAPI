from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from task.database import Base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

class TaskStatus(str, enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS  = "In Progress"
    IN_REVIEW = "In Review"
    REVIEWED = "Reviewed"
    COMPLETED = "Compelted"

class Priority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key= True, index=True)
    username =Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password =Column(String)

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    members = relationship('User',secondary='team_members')

class TeamMember(Base):
    __tablename__ = "team_members"
    team_id = Column(Integer, ForeignKey('teams.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role = Column(String)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    decriptions = Column(String)
    status = Column(Enum(TaskStatus),default=TaskStatus.NOT_STARTED)
    Priority = Column(Enum(Priority),default=Priority.MEDIUM)
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator_id = Column(Integer, ForeignKey('users.id'))
    assignee_id = Column(Integer, ForeignKey('users.id'))
    reviewer_id = Column(Integer, ForeignKey('users.id'))
    
    

