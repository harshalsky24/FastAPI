# from fastapi import APIRouter
# from fastapi import  Depends
# from ..schemas import TaskCreate, TaskOut
# from ..models import TaskStatus
# from ..auth import get_current_user


# router = APIRouter()


# @router.post("/tasks", response_model=TaskOut)
# def create_task(task: TaskCreate,):
    
#     return TaskOut(id=1, title=task.title, description=task.description, 
#                    status=TaskStatus.NOT_STARTED, priority=task.priority, 
#                    deadline=task.deadline)