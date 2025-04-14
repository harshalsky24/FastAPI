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
    """
        Method to create a new team.
        
        This API checks if a team with the same name already exists, and if not, it creates a new team.
        
        Method: POST
        Response: Returns a success message and the created team's details if the team is successfully created.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create team")
    
    exist_team = db.query(Team).filter(Team.name == team.name).first()
    if exist_team:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Team with this name already exist")
    
    new_team = Team(name=team.name,organization_id =team.organization_id)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    
    return {'message':'Team created Successfully.','team':new_team}


@router.post("/team/{team_id}/add-member", response_model=ResponseMessage)
def add_team_member(team_id: int, 
                    request: TeamMemberAddRequest, 
                    db: Session = Depends(get_db), 
                    current_user: dict = Depends(get_current_user)):
    """
        Method to add a user as a member to an existing team.
        
        This API checks if the team exists, validates the user and role, 
        and adds the user as a team member with the specified role.
        
        Method: POST
        Response: Returns a success message on successfully adding a member to the team.
    """
    
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to Add team Member")
    
        team = db.query(Team).filter(Team.id == team_id).first()

        if not team:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team not found")

        user = db.query(User).filter(User.id == request.user_id).first()
        # role = db.query(Role).filter(Role.id == request.role_id).first()

        # if not user or not role:
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user or role ID")

        if db.query(TeamMembership).filter(TeamMembership.user_id == user.id, TeamMembership.team_id == team.id).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member of the team")

        new_membership = TeamMembership(user_id=user.id, team_id=team.id)
        db.add(new_membership)
        db.commit()

        return {"message": "User added to team successfully"}
    
    except Exception as e:
        return {"message": str(e)}
    except Exception as e:
        # Log or handle other exceptions
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    

@router.delete("/team/{team_id}/remove-member", response_model= ResponseMessage)
def remove_member(team_id:int, request: TeamRemoveMember, db:Session=Depends(get_db),
                  current_user: User = Depends(get_current_user)):
        """
            Method to remove a user from a team.
            
            This API checks if the team and user exist, and if the user is a member of the team.
            If the user is a member, they are removed from the team.
            
            Method: DELETE
            Response: Returns a success message if the user is removed from the team.
        """
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to Reamove team Member")
        # breakpoint()
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
        return {"message": "User Deleted from the team successfully"}