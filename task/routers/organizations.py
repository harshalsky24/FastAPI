
from fastapi import APIRouter, Depends, HTTPException, status
from task.schemas import OrganizationCreate
from sqlalchemy.orm import Session
from task.models import User
from task.auth import get_current_user
from task.database import get_db
from task.routers.dependency import is_admin,is_super_admin
from task.models import Organization

router = APIRouter(tags=['Organization'])


@router.post("/organization/create")
def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Only Super Admin can create organizations")
    # breakpoint()
    existing_org = db.query(Organization).filter_by(name=org_data.name).first()
    print(existing_org)
    print(Organization.name)
    if existing_org:
        raise HTTPException(status_code=400, detail="Organization already exists")

    new_org = Organization(name=org_data.name, super_admin_id=current_user.id)
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    return {"message": "Organization created successfully", "organization": new_org.name, "organization_id": new_org.id}



@router.post("/organizations/{org_id}/add_user/{user_id}")
def assign_user_to_org(org_id: int, user_id: int, db: Session = Depends(get_db), current_admin: User = Depends(is_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.organization_id = org_id
    db.commit()
    return {"message": "User assigned to organization"}
