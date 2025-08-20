"""
Created by Fabian Gnatzig

Description: HTTP Routes of team.
"""
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from dependencies import get_session
from models.team_models import Team, TeamUpdate
from models.user_models import get_public_user

router = APIRouter(
    prefix="/team",
    tags=["Team"]
)

@router.get("/all")
def read_all_teams(
        session: Session = Depends(get_session),
        offset: int = 0,
        limit: Annotated[int, Query(le=100)]=100,
) -> Sequence[Team]:
    """
    Reads all team instances.
    :param session: The db session.
    :param offset: The start offset.
    :param limit: The maximum query.
    :return: List of all teams.
    """
    statement = select(Team).offset(offset).limit(limit)
    teams = session.exec(statement).all()
    return teams

@router.post("/add")
def create_team(team: Team, session: Session = Depends(get_session)) -> Team:
    """
    Creates a team instance.
    :param team: The team instance.
    :param session: The db session.
    :return: The created team instance.
    """
    if not team.name:
        raise HTTPException(status_code=400, detail="Incomplete team")

    session.add(team)
    session.commit()
    session.refresh(team)
    return team

@router.get("/{team_id}")
def read_team_id(team_id: int, session: Session = Depends(get_session)) -> dict:
    """
    Searches for a team with id.
    :param team_id: The id of a team to search for.
    :param session: The db session.
    :return: Dictionary with team and users.
    """
    team = session.get(Team, team_id)

    if not team:
        raise HTTPException(status_code=404, detail=f"Team with id '{team_id}' not found!")

    team_json = team.model_dump()
    if team.users:
        public_users=[]
        for user in team.users:
            public_users.append(get_public_user(user))
        team_json.update({"users": public_users})
    if team.seasons:
        team_json.update({"seasons": team.seasons})
    return team_json


@router.get("/name/{team_name}")
def read_team_name(team_name: str, session: Session = Depends(get_session)) -> dict:
    """
    Searches for a team with name.
    :param team_name: The name of a team to search for.
    :param session: The db session.
    :return: Dictionary with team and users.
    """
    statement = select(Team).where(Team.name == team_name)
    try:
        team = session.exec(statement).one()
    except Exception as ex:
        raise HTTPException(
            status_code=404, detail=f"Team with name '{team_name}' not found!") from ex

    if not team:
        raise HTTPException(status_code=404, detail=f"Team with name '{team_name}' not found!")

    team_json = team.model_dump()
    if team.users:
        public_users = []
        for user in team.users:
            public_users.append(get_public_user(user))
        team_json.update({"users": public_users})
    if team.seasons:
        team_json.update({"seasons": team.seasons})
    return team_json

@router.delete("/{team_id}")
def delete_team(team_id: int, session: Session = Depends(get_session)):
    """
    Deletes a team with id.
    :param team_id: The id of a team to be deleted.
    :param session: The db session.
    :return: "ok": True if succeeded.
    """
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team with id '{team_id}' not found!")

    session.delete(team)
    session.commit()
    return {"ok": True}


@router.patch("/{team_id}")
def update_team(
        team_id: int,
        team: TeamUpdate,
        session: Session = Depends(get_session)
) -> Team:
    """
    Updates the data of a team.
    :param team_id: The id of a team to be edited.
    :param team: The edited team data.
    :param session: The db session.
    :return: The edited team instance.
    """
    team_db = session.get(Team, team_id)
    if not team_db:
        raise HTTPException(status_code=404, detail=f"Team with id '{team_id}' not found!")

    team_data = team.model_dump(exclude_unset=True)
    team_db.sqlmodel_update(team_data)
    session.add(team_db)
    session.commit()
    session.refresh(team_db)
    return team_db
