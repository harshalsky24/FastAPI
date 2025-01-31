from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Task, Team, TaskStatus, TeamMembership
from ..auth import get_current_user

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard/user-dashboard")
def user_dashboard(db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)):
    
    """
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

    recent_tasks = db.query(Task).order_by(Task.created_at.desc()).limit(5).all()
    recent_users = db.query(User).order_by(User.id.desc()).limit(5).all()
    recent_teams = db.query(Team).order_by(Team.id.desc()).limit(5).all()


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
