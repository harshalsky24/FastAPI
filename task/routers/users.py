from fastapi import APIRouter, Depends, HTTPException
from ..schemas import UserBase, UserOut, UserCreate, UserLogin, Token
from sqlalchemy.orm import session
from ..hashing import get_password_hash,verify_password
from ..auth import create_access_token
from ..models import User, UserRole, Role
from sqlalchemy.orm import Session
from ..database import SessionLocal


router = APIRouter(tags=["User"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserOut)
def register(user:UserCreate, db: session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(username = user.username,email = user.email, hashed_password = hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login",response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Generate JWT token using user ID
    access_token = create_access_token({"sub": str(db_user.id)})

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/roles/")
def create_role(role_name: UserRole, db: Session = Depends(get_db)):
    db_role = Role(role_name=role_name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return {"message": "Role created successfully", "role": db_role.role_name}

