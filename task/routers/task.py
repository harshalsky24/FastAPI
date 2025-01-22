


from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from ..models import Task, Team, TeamMembership
from ..schemas import TaskCreate, TaskOut
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()

@router.post("/teams/{team_id}/tasks", response_model=TaskOut)
def create_task(
    team_id: int, 
    task_data: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check if the team exists
        breakpoint()
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

        # Check user role in the team (admin/manager)
        team_membership = db.query(TeamMembership).filter(
            TeamMembership.team_id == team_id,
            TeamMembership.user_id == current_user.id
        ).first()

        if not team_membership or team_membership.role not in ['admin', 'manager']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to create tasks in this team.")

        # Check if a task with the same title already exists
        existing_task = db.query(Task).filter(Task.title == task_data.title).first()
        if existing_task:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task with this title already exists.")

        # Create new task
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            deadline=task_data.deadline,
            creator_id=current_user.id,
            team_id=team_id,
            reviewer_id=task_data.reviewer_id,
            assignee_id=task_data.assignee_id
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return {
            "message": "Task created successfully!",
            "task": new_task
        }
    except HTTPException as http_err:
        raise http_err  # re-raise HTTP exceptions
    except Exception as e:
        # Log the exception and raise a generic error message
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the task.")
