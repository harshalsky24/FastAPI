from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from task.models import Permission, User, TeamMembership
from task.schemas import PermissionSchema
from task.routers.dependency import is_admin
from task.database import get_db
from task.auth import get_current_user

router = APIRouter()

def check_user_permission(user_id: int, db: Session = Depends(get_db)):
    """
    Check if the user has write permission before allowing task creation.
    """
    # Fetch user details
    # breakpoint()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # # Admins can create tasks without checking permissions
    # if user.role == "Admin":
    #     return True

    # Fetch user permissions from the Permission table
    permissions = db.query(Permission).filter(Permission.user_id == TeamMembership.user_id).first()
    print(permissions)
    # if not permissions:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissions not assigned to this user")
    print(permissions.write)
    # Check if the user has write permission
    print(permissions.update)
    if not permissions.write:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have write permission to create a task"
        )
    elif not permissions.update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have update permission to modify a task"
        )
    return True

@router.post("/assign-permission")
def assign_permission(
    request: PermissionSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user_id = current_user.id
    # Ensure only Admin can assign permissions
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to assign permissions")

    # Check if the user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    team_membership = (
        db.query(TeamMembership)
        .filter(TeamMembership.user_id == request.user_id)
        .first()
    )
    print(request.user_id)

    if not team_membership:
        raise HTTPException(status_code=400, detail="User is not a member of any team")

    # Check if permission entry already exists for the user
    permission = db.query(Permission).filter(Permission.user_id == request.user_id).first()

    if permission:
        permission.read = request.read
        permission.write = request.write
        permission.update = request.update
    else:
        new_permission = Permission(
            user_id=request.user_id,
            read=request.read,
            write=request.write,
            update=request.update
        )
        db.add(new_permission)

    db.commit()
    return {"message": "Permissions assigned successfully"}

