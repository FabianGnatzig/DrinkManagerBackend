"""
Created by Fabian Gnatzig
Description: Http routes of bring beers.
"""

from typing import Sequence, Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from auth.auth_methods import auth_is_admin
from dependencies import get_session, oauth2_scheme
from exceptions import NotFoundException
from models.beer_models import BringBeer, BringBeerUpdate

router = APIRouter(prefix="/bringbeer", tags=["BringBeer"])

TYPE = "BRING_BEER"


@router.get("/all")
def read_bring_beers(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[BringBeer]:
    """
    Reads all bring beer instances.
    :param session: The db session.
    :param offset: Start offset.
    :param limit: Query limit.
    :return: List of all bring beer instances.
    """
    statements = select(BringBeer).offset(offset).limit(limit)
    bring_beers = session.exec(statements).all()
    return bring_beers


@router.get("/{bring_beer_id}")
def read_bring_beer_id(
    bring_beer_id: int, session: Session = Depends(get_session)
) -> dict:
    """
    Searches for a bring beer with id.
    :param bring_beer_id: ID of a bring beer instance.
    :param session: The db session.
    :return: Dictionary with bring beer and related instances.
    """
    bring_beer = session.get(BringBeer, bring_beer_id)
    if not bring_beer:
        raise NotFoundException(TYPE, data_id=bring_beer_id)

    bring_beer_json = bring_beer.model_dump()
    if bring_beer.user:
        bring_beer_json.update({"user": bring_beer.user.model_dump()})
    if bring_beer.event:
        bring_beer_json.update({"event": bring_beer.event.model_dump()})
    if bring_beer.beer:
        bring_beer_json.update({"beer": bring_beer.beer.model_dump()})
    return bring_beer_json


@router.post("/add")
def create_bring_beer(
    bring_beer: BringBeer, session: Session = Depends(get_session)
) -> BringBeer:
    """
    Creates a bring beer instance.
    :param bring_beer: The bring beer instance.
    :param session: The db session.
    :return: The created bring beer instance.
    """
    session.add(bring_beer)
    session.commit()
    session.refresh(bring_beer)
    return bring_beer


@router.delete("/{bring_beer_id}")
def delete_bring_beer(
    bring_beer_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> dict:
    """
    Deletes a bring beer with id.
    :param bring_beer_id: ID of bring beer instance.
    :param token: User jwt-token.
    :param session: The db session.
    :return: {"ok": True} if succeeded.
    """
    auth_is_admin(token)

    bring_beer = session.get(BringBeer, bring_beer_id)
    if not bring_beer:
        raise NotFoundException(TYPE, data_id=bring_beer_id)

    session.delete(bring_beer)
    session.commit()
    return {"ok": True}


@router.patch("/{bring_beer_id}")
def update_bring_beer(
    bring_beer_id: int,
    bring_beer: BringBeerUpdate,
    session: Session = Depends(get_session),
) -> BringBeer:
    """
    Updates the data of a bring beer instance.
    :param bring_beer_id: ID of the bring beer to be edited.
    :param bring_beer: The edited bring beer data.
    :param session: The db session.
    :return: The edited bring beer instance.
    """
    bring_beer_db = session.get(BringBeer, bring_beer_id)
    if not bring_beer_db:
        raise NotFoundException(TYPE, data_id=bring_beer_id)

    bring_beer_data = bring_beer.model_dump(exclude_unset=True)
    bring_beer_db.sqlmodel_update(bring_beer_data)
    session.add(bring_beer_db)
    session.commit()
    session.refresh(bring_beer_db)
    return bring_beer_db


@router.get("/done/{bring_beer_id}")
def set_bring_beer_done(bring_beer_id: int, session: Session = Depends(get_session)):
    """
    Set the bring beer to done.
    :param bring_beer_id: ID of bring beer.
    :param session: DB session.
    :return: None
    """
    bring_beer_update = BringBeerUpdate(done="True")
    update_bring_beer(bring_beer_id, bring_beer_update, session=session)
