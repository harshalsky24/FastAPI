from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas import TeamCreate, TeamResponse, TeamMemberAddRequest, ResponseMessage, TeamRemoveMember
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import Team, TeamMembership, User, Role

router = APIRouter(tags=['Team'])


@router.post("/team-create")
def create_team(team: TeamCreate,db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    exist_team = db.query(Team).filter(Team.name == team.name).first()
    if exist_team:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Team with this name already exist")
    
    new_team = Team(name=team.name)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    
    return {'message':'Team created Successfully.','team':new_team}


@router.post("/team/{team_id}/add-member", response_model=ResponseMessage)
def add_team_member(team_id: int, 
                    request: TeamMemberAddRequest, 
                    db: Session = Depends(get_db), 
                    current_user: dict = Depends(get_current_user)):
    try:
        team = db.query(Team).filter(Team.id == team_id).first()

        if not team:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team not found")

        user = db.query(User).filter(User.id == request.user_id).first()
        role = db.query(Role).filter(Role.id == request.role_id).first()

        if not user or not role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user or role ID")

        if db.query(TeamMembership).filter(TeamMembership.user_id == user.id, TeamMembership.team_id == team.id).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member of the team")

        new_membership = TeamMembership(user_id=user.id, team_id=team.id, role_id=role.id)
        db.add(new_membership)
        db.commit()

        return {"message": "User added to team successfully"}
    
    except Exception as e:
        return {"message": str(e)}
    

@router.delete("/team/{team_id}/remove-member", response_model= ResponseMessage)
def remove_member(team_id:int, request: TeamRemoveMember, db:Session=Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    try:
        team = db.query(Team).filter(Team.id == team_id).first()

        if not team:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team not found")
        
        user = db.query(User).filter(User.id == request.user_id).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, deatisl="Invalid user ID")
        
        member = db.query(TeamMembership).filter(TeamMembership.user_id == user.id,TeamMembership.team_id == team.id).first()
        if not member:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a member of team")
        
        db.delete(member)
        db.commit()
    except Exception as e:
        return {"message": str(e)}