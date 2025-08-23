"""
Created by Fabian Gnatzig

Description: HTTP routes of season.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from dependencies import get_session
from models.season_models import Season, SeasonUpdate

router = APIRouter(prefix="/season", tags=["Season"])


@router.get("/all")
def read_all_seasons(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list:
    """
    Reads all season instances.
    :param session: The db session.
    :param offset: The start offset.
    :param limit: The maximum query.
    :return: List of all seasons.
    """
    statement = select(Season).offset(offset).limit(limit)
    seasons_data = session.exec(statement).all()
    seasons = []
    for season in seasons_data:
        season_data = season.model_dump()
        if season.team:
            season_data.update({"team": season.team.model_dump()})
        seasons.append(season_data)
    return seasons


@router.get("/{season_id}")
def get_season_id(season_id: int, session: Session = Depends(get_session)) -> dict:
    """
    Searches for a season with id.
    :param season_id: The id of a season to search for.
    :param session: The db session.
    :return: Dictionary with season and team.
    """
    season = session.get(Season, season_id)
    if not season:
        raise HTTPException(
            status_code=404, detail=f"Season with id '{season_id}' not found!"
        )

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
    :param season_name: The name of a season to search for.
    :param session: The db session.
    :return: Dictionary with season and team.
    """
    statement = select(Season).where(Season.name == season_name)
    try:
        season = session.exec(statement).one()
    except Exception as ex:
        raise HTTPException(
            status_code=404, detail=f"Season with name '{season_name}' not found!"
        ) from ex

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
    :param season: The season instance.
    :param session: The db session.
    :return: The created season instance.
    """
    if not (season.name and season.team_id):
        raise HTTPException(status_code=400, detail="Invalid season")

    session.add(season)
    session.commit()
    session.refresh(season)
    return season


@router.delete("/{season_id}")
def delete_season(season_id: int, session: Session = Depends(get_session)) -> dict:
    """
    Deletes a season with id.
    :param season_id: The id of a season to be deleted.
    :param session: The db session.
    :return: {"ok": True} if succeeded.
    """
    season = session.get(Season, season_id)
    if not season:
        raise HTTPException(
            status_code=404, detail=f"Season with id '{season_id}' not found!"
        )

    session.delete(season)
    session.commit()
    return {"ok": True}


@router.patch("/{season_id}")
def update_season(
    season_id: int, season: SeasonUpdate, session: Session = Depends(get_session)
) -> Season:
    """
    Updates the data of a season.
    :param season_id: The id of the season to be edited.
    :param season: The edited season data.
    :param session: The db session.
    :return: The edited season instance.
    """
    season_db = session.get(Season, season_id)
    if not season_db:
        raise HTTPException(
            status_code=404, detail=f"Season with id '{season_id}' not found!"
        )

    season_data = season.model_dump(exclude_unset=True)
    season_db.sqlmodel_update(season_data)
    session.add(season_db)
    session.commit()
    session.refresh(season_db)
    return season_db
