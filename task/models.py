from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Boolean, Table
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

class PriorityStatus(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Role(enum.Enum):
    admin = "admin"
    manager = "manager"
    member = "member"

#many to many relationship
team_members_many = Table(
    'team_members_many',
    Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id', ondelete="CASCADE")),
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE"))
)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key= True, index=True)
    username =Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password =Column(String)
    
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.creator_id")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    review_tasks = relationship("Task", back_populates="reviewer", foreign_keys="Task.reviewer_id")
    teams = relationship("Team", secondary=team_members_many, back_populates="members")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(Enum(Role), unique=True, nullable=False)
class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    members = relationship("User", secondary=team_members_many, back_populates="teams")
    tasks = relationship("Task", back_populates="team")

class TeamMember(Base):
    __tablename__ = "team_members"
    team_id = Column(Integer, ForeignKey('teams.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role = Column(String)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(Enum(TaskStatus),default=TaskStatus.NOT_STARTED)
    priority = Column(Enum(PriorityStatus),default=PriorityStatus.MEDIUM)
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    reviewer = relationship("User", back_populates="review_tasks", foreign_keys=[reviewer_id])
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[creator_id])
    team = relationship("Team", back_populates="tasks")

class TeamMembership(Base):
    __tablename__ = "team_memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User")
    team = relationship("Team")
    role = relationship("Role")