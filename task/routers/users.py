from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas import UserBase, UserOut, UserCreate, UserLogin, Token, RoleCreateRequest, SuperUserCreate
from sqlalchemy.orm import session
from ..hashing import get_password_hash,verify_password, generate_random_password
from ..auth import create_access_token, get_current_user, create_refresh_token
from ..models import User, UserRole, Role, TeamMembership
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from task.models import User, Organization
from ..database import SessionLocal
from .invite import send_invite_email


router = APIRouter(tags=["User"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register/super_admin")
def register_super_admin(user: SuperUserCreate, db: Session = Depends(get_db)):
    """
    Register the first Super Admin.
    
    - Ensures only one Super Admin exists.
    - Assigns "super_admin" role to the first user.
    """
    # breakpoint()
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    super_admin = User(
        email=user.email,
        hashed_password=hashed_password,
        role="super_admin"
    )
    db.add(super_admin)
    db.commit()
    db.refresh(super_admin)
    
    return {"message": "Super Admin registered successfully", "email": super_admin.email}


@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - First user in an organization becomes 'Admin'.
    - Subsequent users are assigned 'Member' role.
    - Only 'Admin' can register 'Member' users in their organization.
    - Users cannot see other organizations' data.
    """
    try:
        # Check if the organization exists
        organization = db.query(Organization).filter(Organization.id == user.organization_id).first()
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Determine role (First user = Admin, others = Member)
        existing_users = db.query(User).filter(User.organization_id == user.organization_id).count()
        role = "admin" if existing_users == 0 else "member"

        # Ensure the email is unique
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password and create user
        hashed_password = get_password_hash(user.password)
        new_user = User(
            email=user.email,
            hashed_password=hashed_password,
            role=role,
            organization_id=user.organization_id
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Send invite email
        send_invite_email(user.email, user.password)
        print("Invitation sent")

        return new_user

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/super_admin_login",response_model=Token)
def super_admin_login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if db_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Access denied. Super Admins only.")
    # Generate both access and refresh tokens
    access_token = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})

    return {"message": "success", "access_token": access_token,
            "refresh_token": refresh_token,"token_type": "bearer", "role": db_user.role}

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
    
    # team_membership = db.query(TeamMembership).filter(TeamMembership.user_id == db_user.id).first()
    # role_id = team_membership.role_id if team_membership else None  # Handle case where user has no team

    # Generate JWT token using user ID
    access_token = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})

    return {"message": "success", "access_token": access_token,
            "refresh_token": refresh_token,"token_type": "bearer"}

@router.post("/roles")
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

@router.post("/admin/login")
def admin_login(user: UserLogin, db: Session = Depends(get_db)):
    # breakpoint()
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if db_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")
    # Generate both access and refresh tokens
    access_token = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})

    return {"message": "success", "access_token": access_token,
            "refresh_token": refresh_token,"token_type": "bearer"}

@router.get("/users")
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Get the organization_id of the current admin
    organization_id = current_user.organization_id
    
    # Query users from the same organization with role 'Member', excluding 'Admin' role
    users = db.query(User).filter(User.organization_id == organization_id, User.role != "admin").all()
    
    # Return only user details (id and email)
    return [{"id": user.id, "email": user.email} for user in users]