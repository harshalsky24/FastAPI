from fastapi import APIRouter, HTTPException, status, Depends ,Query
from sqlalchemy.orm import Session
from ..models import Task, Team, TeamMembership, User
from ..schemas import TaskCreate, TaskOut, TaskResponse, TaskUpdateRequest, DeleteTaskRequest, TaskResponseSchema
from ..database import get_db
from ..auth import get_current_user
from typing import List, Optional

router = APIRouter(tags=['Task'])

@router.post("/task/{team_id}/create-task", response_model=TaskOut)
def create_task(
    team_id: int, 
    task_data: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        
        user_id = current_user.id 
        print(user_id) # Access user ID correctly
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

        team_membership = (db.query(TeamMembership).filter(TeamMembership.team_id == team.id, 
                                                           TeamMembership.user_id == current_user.id).first())
        
        if (
            team_membership.role.role_name != "admin" and
            team_membership.role.role_name != "manager"
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you do not have permission to edit this task")

        existing_task = db.query(Task).filter(Task.title == task_data.title).first()
        if existing_task:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task with this title already exists.")

        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            deadline=task_data.deadline,
            creator_id=user_id,
            team_id=team_id,
            reviewer_id=task_data.reviewer_id,
            assignee_id=task_data.assignee_id
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return new_task
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the task.")

@router.put("/task/{team_id}/update-task", response_model=TaskResponse)
def update_task(team_id: int, request: TaskUpdateRequest, 
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    try:
        
        current_user_id = current_user.id 
        team = db.query(Team).filter(Team.id == team_id).first()
        print(team)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
        task = db.query(Task).filter(Task.id == request.task_id).first()
        print(task)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
        if task.team_id != team.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The task does not belog to the specificed team.")
        
        team_membership = (db.query(TeamMembership).filter(TeamMembership.team_id == team.id, 
                                                           TeamMembership.user_id == current_user_id)
                                                           .first())
        if not team_membership:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not a member of this team")
        
        if (
            current_user_id != task.assignee_id and 
            current_user_id != task.reviewer_id and
            team_membership.role.role_name != "manager"
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you do not have permission to edit this task")

        if request.description:
            task.description = request.description
        if request.priority:
            task.priority = request.priority
        if request.assignee_id:
            assignee = db.query(User).filter(User.id == request.assignee_id).first()
            if not assignee:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee not found")
            task.assignee_id = assignee.id

        db.commit()
        db.refresh(task)
        return task
    
    except Exception as e:
        return {"message": str(e)}


@router.delete("/task/{team_id}/delete-task")
def delete_task(team_id: int,
                request: DeleteTaskRequest, 
                db: Session = Depends(get_db), 
                current_user: User = Depends(get_current_user)):
    try:
        task_id = request.task_id
    
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
        task =db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
        team_membership = (db.query(TeamMembership).filter(TeamMembership.team_id == team.id, 
                                                           TeamMembership.user_id == current_user.id)
                                                           .first())
        if (team_membership.role.role_name != "admin" and team_membership.role.role_name != "manager"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                                detail="you do not have permission to edit this task")
        db.delete(task)
        db.commit()
        return {"message": "Task Deleted"}
    except Exception as e:
        return {"message": str(e)}


@router.get("/task/sortfilter", response_model=List[TaskResponseSchema])
def sortfilter(
    db: Session = Depends(get_db),  
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[str] = Query(None, description="Filter by task priority"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    sort_by: Optional[str] = Query("created_at", description="Sort field (e.g., deadline, created_at)"),
    order: Optional[str] = Query("asc", description="Sort order: asc or desc"),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task)

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)


    sort_column = getattr(Task, sort_by, Task.created_at)  # Default to created_at if invalid
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column)

    tasks = query.all()
    return tasks