from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi.templating import Jinja2Templates
from ..models import User, Task, Team, TaskStatus, TeamMembership
from ..auth import get_current_user
from ..schemas import UserOut
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="task/templates")

@router.get("/dashboard/user-dashboard")
def user_dashboard(db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)):
    
    """
        Access: Current user
        Retrieves the user dashboard with an overview of tasks.
        Method: GET
        Response: All the records shows from assigned tasks, created tasks, review tasks.
    """
    assigned_tasks = db.query(Task).filter(Task.assignee_id == current_user.id).all()

    created_tasks = db.query(Task).filter(Task.creator_id == current_user.id).all()

    review_tasks = db.query(Task).filter(Task.reviewer_id == current_user.id).all()


    dashboard_data = {
        "user_id": current_user.id,
        "user_name": current_user.username,
        "assigned_tasks": assigned_tasks,
        "created_tasks": created_tasks,
        "review_tasks": review_tasks,
    }

    return dashboard_data



@router.get("/dashboard/admin-dashboard")
def admin_dashboard(db:Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
    """
    Retrieves the admin dashboard with an overview of tasks, users, and teams.

    Access: Admin only.
    Method: GET
    Response: Total counts of tasks, users, and teams.
              Recent tasks, users, and teams (latest 5 records).
    """
    team_membership = (db.query(TeamMembership).filter( TeamMembership.user_id == current_user.id).first())
    if team_membership.role.role_name != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                                detail="you do not have permission to access.")
    
    total_tasks = db.query(Task).count()
    total_user = db.query(User).count()
    total_team = db.query(Team).count()

    recent_tasks = db.query(Task).order_by(Task.created_at.desc()).all()
    recent_users = db.query(User).order_by(User.id.desc()).all()
    recent_teams = db.query(Team).order_by(Team.id.desc()).all()


    all_data={
        "total_counts":{
            "total_tasks": total_tasks,
            "total_users": total_user,
            "total_team": total_team
        },
        "all_data":{
            "Tasks": recent_tasks,
            "users": recent_users,
            "teams": recent_teams
        }
    }
    return all_data


@router.get("/dashboard/team-dashboard/{team_id}")
def team_dashboard(team_id: int, db:Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
    """
        Retrieves the team dashboard with an overview of tasks assigned to the current user.

        Access: Team members only.
        Method: GET
        Path Parameter: team_id (int): The ID of the team whose dashboard is being accessed.
        Response: Lists all tasks assigned to the user within the specified team.

    """
    # breakpoint()
    user_id = current_user.id
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    is_member = (
        db.query(TeamMembership)
        .filter(TeamMembership.team_id == team_id, TeamMembership.user_id == current_user.id)
        .first()
    )

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not a member of this team"
        )
    
    all_assigned_tasks = db.query(Task).filter(Task.assignee_id == user_id).all()
    in_assigned_tasks = db.query(Task).filter(Task.assignee_id == user_id, Task.status == TaskStatus.IN_PROGRESS).all()
    awaiting_assigned_tasks = db.query(Task).filter(Task.assignee_id == user_id, Task.status == TaskStatus.IN_REVIEW).all()

    all_data = {
        "all_assigned_task": all_assigned_tasks,
        "in_process_tasks": in_assigned_tasks,
        "awaiting_assigned_tasks": awaiting_assigned_tasks
    }
    
    return all_data


@router.get("/organization/dashboard",)
async def dashboard_page(db:Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Ensure that the user has an organization_id and is the admin of that organization
    if not current_user.organization_id:
        raise HTTPException(status_code=403, detail="User not part of any organization")

    # Fetch data for the current user's organization
    # Users, tasks, and teams are all filtered by the organization_id of the logged-in user
    users = db.query(User).filter(User.organization_id == current_user.organization_id).all()
    tasks = db.query(Task).filter(Task.organization_id == current_user.organization_id).all()
    teams = db.query(Team).filter(Team.organization_id == current_user.organization_id).all()

    all_data = {
        "users": users,
        "tasks": tasks,
        "teams": teams
    }
    return all_data