from fastapi import APIRouter, HTTPException, status, Depends ,Query
from sqlalchemy.orm import Session
from task.models import Task, Team, TeamMembership, User
from task.schemas import TaskCreate, TaskOut, TaskResponse, TaskUpdateRequest, DeleteTaskRequest, TaskResponseSchema
from task.database import get_db
from task.auth import get_current_user
from typing import List, Optional
from task.utils.websocket_manager import manager
from task.routers.permissions import check_user_permission
router = APIRouter(tags=['Task'])

@router.post("/task/{team_id}/create-task", response_model=TaskOut)
def create_task(
    team_id: int, 
    task_data: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    """
        Method to create a new task within a team.
        
        This API allows users with admin or manager roles within a team to create new tasks.
        It checks if the team exists, if the user has the necessary permissions, 
        and if a task with the same title already exists in the team.
        
        Method: POST
        Response: Returns the newly created task details upon successful creation.
        Permissions: Only users with 'admin' or 'manager' roles in the team can create tasks.
    """
        
    user_id = current_user.id 
    print(user_id) # Access user ID correctly
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found")
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    user = (db.query(User).filter(User.id == current_user.id).first())
    
    if (
        user.role != "admin" 
        # and
        # team_membership.role.role_name != "manager"
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you do not have permission to edit this task")

    existing_task = db.query(Task).filter(Task.title == task_data.title).first()
    if existing_task:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task with this title already exists.")
    
    # check_user_permission(current_user.id,db)
    # print(current_user.id)
    
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        deadline=task_data.deadline,
        creator_id=user_id,
        team_id=team_id,
        reviewer_id=task_data.reviewer_id,
        assignee_id=task_data.assignee_id,
        organization_id=task_data.organization_id,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task
    
@router.put("/task/{team_id}/update-task", response_model=TaskResponse)
async def update_task(team_id: int, request: TaskUpdateRequest, 
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    """
        Method to update an existing task within a team.
        
        This API allows users to update task details such as description, priority, status, 
        and assignee. The user must be either the assignee, reviewer, 
        or have a manager role in the team.
        
        Method: PUT
        Response: Returns the updated task details.
        Permissions: Only the assignee, reviewer, or users with a 'manager' role can update the task.
        Error Handling: If the team or task does not exist, a 404 error is returned.
                        If the user is not part of the team or lacks the necessary permissions, 
                        a 403 error is returned.
                        If the assignee provided is invalid, a 404 error is returned.
        Real-Time Notifications: Sends WebSocket notifications to team members 
                                 if task assignee or status changes.
    """
    
    current_user_id = current_user.id 
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    
    task = db.query(Task).filter(Task.id == request.task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if task.team_id != team.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The task does not belong to the specified team.")
    
    # team_membership = db.query(TeamMembership).filter(
    #     TeamMembership.team_id == team.id, 
    #     TeamMembership.user_id == current_user_id
    # ).first()

    # if not team_membership:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this team")

    # if (
    #     current_user_id != task.assignee_id and 
    #     current_user_id != task.reviewer_id and
    #     team_membership.role.role_name != "manager"
    # ):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to edit this task")

    check_user_permission(current_user_id,db)
    # Store old values before updating
    old_assignee = task.assignee_id
    old_status = task.status
    # task.assignee_id = task_data.assignee_id
    # task.status = task_data.status

    # Update Task Fields
    if request.description:
        task.description = request.description
    if request.priority:
        task.priority = request.priority
    if request.status:
        task.status = request.status  # Allow updating status
    if request.assignee_id:
        assignee = db.query(User).filter(User.id == request.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee not found")
        task.assignee_id = assignee.id

    db.commit()
    db.refresh(task)
    # breakpoint()
    # **Send Real-Time Notifications via WebSockets**
    notification_messages = []

    # Notify Assignee Change (if changed)
    if old_assignee != task.assignee_id:
        notification_messages.append({
            "users": [old_assignee, task.assignee_id],  
            "message": f"Task {task.id} was reassigned to a user {task.assignee_id}."
        })

    # Notify Task Status Change (if changed)
    if old_status != task.status:
        assigned_users = {task.assignee_id, task.reviewer_id}  

        # Get all team members
        team_members = db.query(TeamMembership).filter(TeamMembership.team_id == task.team_id).all()
        for member in team_members:
            assigned_users.add(member.user_id)

        notification_messages.append({
            "users": list(assigned_users),
            "message": f"Task {task.id} status changed from {old_status} to {task.status}."
        })

    # Send WebSocket notifications
    for notif in notification_messages:
        print(f"Sending notification: {notif['message']} to users {notif['users']}")
        await manager.broadcast_to_team(notif["users"], notif["message"])
    

    return task


@router.delete("/task/{team_id}/delete-task")
def delete_task(team_id: int,
                request: DeleteTaskRequest, 
                db: Session = Depends(get_db), 
                current_user: User = Depends(get_current_user)):
    """
        Deletes a task from a specific team.

        This endpoint allows admins and managers to delete tasks from a given team.
        
        Method: DELETE
        Path Parameters: team_id (int): The ID of the team from which the task should be deleted.
        Request Body: task_id (int): The ID of the task to be deleted.
        Response: A success message confirming task deletion.
        Permissions: Only users with the role of admin or manager can delete tasks.
    """
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
    current_user: User = Depends(get_current_user)):

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