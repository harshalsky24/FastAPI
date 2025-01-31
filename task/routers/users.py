from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas import UserBase, UserOut, UserCreate, UserLogin, Token, RoleCreateRequest
from sqlalchemy.orm import session
from ..hashing import get_password_hash,verify_password
from ..auth import create_access_token, get_current_user
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
    """
        Register a new user in the system.

        This endpoint allows a user to register by providing a unique username, email, and password.
        The password is hashed before storing in the database for security.

        Parameters:
            user(UserCreate): The user information required to register a new user (username, email, password).
            db(session): The database session used to interact with the database.

        Responses:
            201 Created: If the registration is successful, the newly created user's information is returned.
            400 Bad Request: If the username already exists in the database.
            500 Internal Server Error: If an unexpected error occurs during the registration process.
    """
    try:
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Username already exists")
        #hashed the password
        hashed_password = get_password_hash(user.password)
        db_user = User(username = user.username,email = user.email, hashed_password = hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
@router.post("/login",response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
        Authenticate a user and generate a JWT token.

        This endpoint allows users to log in using their email and password. If the credentials 
        are valid, a JWT access token is generated and returned.

        Parameters:
            user(UserLogin): The login credentials containing email and password.
            db(Session): The database session used to fetch user details.

        Responses:
            200 OK: Returns a JWT token upon successful authentication.
            400 Bad Request: If the email or password is incorrect.

    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Generate JWT token using user ID
    access_token = create_access_token({"sub": str(db_user.id)})

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/roles/")
def create_role(role_request: RoleCreateRequest, role_name: UserRole, db: Session = Depends(get_db), 
                current_user: User= Depends(get_current_user)):
    """
        Create a new user role.
        This endpoint allows an authenticated user to create a new role in the system.

        Parameters:
            role_request (RoleCreateRequest): The request body containing role details.
            role_name (UserRole): The name of the role to be created.
            db(Session): The database session used to store the role.
            current_user(User): The currently authenticated user.

        Responses: 200 OK: Role created successfully.
                   400 Bad Request: If there is an issue with role creation.
    """
    db_role = Role(role_name=role_name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return {"message": "Role created successfully", "role": db_role.role_name}

