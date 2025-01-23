from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Boolean, Table
from sqlalchemy.orm import relationship
from task.database import Base
import enum
from datetime import datetime

# Enums for task status and priority
class TaskStatus(str, enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    REVIEWED = "Reviewed"
    COMPLETED = "Completed"

class PriorityStatus(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"

# Many-to-many relationship table for users and teams
team_members_association = Table(
    'team_members_association',
    Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id', ondelete="CASCADE"), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.creator_id")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    review_tasks = relationship("Task", back_populates="reviewer", foreign_keys="Task.reviewer_id")
    teams = relationship("Team", secondary=team_members_association, back_populates="members")
    memberships = relationship("TeamMembership", back_populates="user")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(Enum(UserRole), unique=True, nullable=False)
    memberships = relationship("TeamMembership", back_populates="role")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    members = relationship("User", secondary=team_members_association, back_populates="teams")
    tasks = relationship("Task", back_populates="team")
    memberships = relationship("TeamMembership", back_populates="team")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(TaskStatus), default=TaskStatus.NOT_STARTED)
    priority = Column(Enum(PriorityStatus), default=PriorityStatus.MEDIUM)
    deadline = Column(DateTime, nullable=False)
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

    user = relationship("User", back_populates="memberships")
    team = relationship("Team", back_populates="memberships")
    role = relationship("Role", back_populates="memberships")