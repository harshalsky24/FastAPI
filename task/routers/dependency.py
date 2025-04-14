from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from task.database import get_db
from task.models import User
from task.auth import get_current_user  # Your authentication function

def is_admin(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user or user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

def is_super_admin(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user or user.role != "Super_Admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user