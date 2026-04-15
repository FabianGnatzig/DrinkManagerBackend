"""
Created by Fabian Gnatzig
Description: HTTP routes of season.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from auth.auth_methods import is_admin, get_team_id
from dependencies import get_session, oauth2_scheme
from exceptions import NotFoundException, IncompleteException, InvalidRoleException
from models.season_models import Season, SeasonUpdate

router = APIRouter(prefix="/season", tags=["Season"])
TYPE = "SEASON"


@router.get("/all")
def read_all_seasons(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> list:
    """
    Reads all season instances.
    :param session: DB session.
    :param token: User jwt-token.
    :return: List of all seasons.
    """
    try:
        is_admin(token)
        statement = select(Season)
    except InvalidRoleException:
        team_id = get_team_id(token)
        statement = select(Season).where(Season.team_id == team_id)

    seasons_data = session.exec(statement).all()
    seasons = []
    for season in seasons_data:
        season_data = season.model_dump()
        if season.team:
            season_data.update({"team": season.team.model_dump()})
        seasons.append(season_data)
    return seasons


@router.get("/{season_id}")
def get_season_id(season_id: uuid.UUID, session: Session = Depends(get_session)) -> dict:
    """
    Searches for a season with ID.
    :param season_id: ID of a season to search for.
    :param session: DB session.
    :return: Dictionary with season and team.
    """
    season = session.get(Season, season_id)
    if not season:
        raise NotFoundException(TYPE, data_id=season_id)

    season_json = season.model_dump()
    if season.team:
        season_json.update({"team": season.team.model_dump()})
    if season.events:
        season_json.update({"events": season.events})
    return season_json


@router.get("/name/{season_name}")
def get_season_name(season_name: str, session: Session = Depends(get_session)) -> dict:
    """
    Searches for a season with name.
    :param season_name: Name of a season to search for.
    :param session: DB session.
    :return: Dictionary with season and team.
    """
    statement = select(Season).where(Season.name == season_name)
    try:
        season = session.exec(statement).one()
    except Exception as ex:
        raise NotFoundException(TYPE, data_name=season_name) from ex

    season_json = season.model_dump()
    if season.team:
        season_json.update({"team": season.team.model_dump()})
    if season.events:
        season_json.update({"events": season.events})
    return season_json


@router.post("/add")
def create_season(season: Season, session: Session = Depends(get_session)) -> Season:
    """
    Creates a season instance.
    :param season: Season instance.
    :param session: DB session.
    :return: Created season instance.
    """
    if not isinstance(season.team_id, uuid.UUID):
        season.team_id = uuid.UUID(season.team_id)

    if not (season.name and season.team_id):
        raise IncompleteException(TYPE)

    session.add(season)
    session.commit()
    session.refresh(season)
    return season


@router.delete("/{season_id}")
def delete_season(
    season_id: uuid.UUID,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> dict:
    """
    Deletes a season with ID.
    :param season_id: ID of a season to be deleted.
    :param token: User jwt-token.
    :param session: DB session.
    :return: {"ok": True} if succeeded.
    """
    is_admin(token)

    season = session.get(Season, season_id)
    if not season:
        raise NotFoundException(TYPE, data_id=season_id)

    session.delete(season)
    session.commit()
    return {"ok": True}


@router.patch("/{season_id}")
def update_season(
    season_id: uuid.UUID, season: SeasonUpdate, session: Session = Depends(get_session)
) -> Season:
    """
    Updates the data of a season.
    :param season_id: ID of the season to be edited.
    :param season: Edited season data.
    :param session: DB session.
    :return: Edited season instance.
    """
    season_db = session.get(Season, season_id)
    if not season_db:
        raise NotFoundException(TYPE, data_id=season_id)

    season_data = season.model_dump(exclude_unset=True)
    season_db.sqlmodel_update(season_data)
    session.commit()
    session.refresh(season_db)
    return season_db
