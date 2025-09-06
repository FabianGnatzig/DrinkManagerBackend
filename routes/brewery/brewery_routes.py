"""
Created by Fabian Gnatzig
Description: HTTP routes of brewery's.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from auth.auth_methods import is_admin
from dependencies import get_session, oauth2_scheme
from exceptions import IncompleteException, NotFoundException
from models.brewery_models import Brewery, BreweryUpdate

router = APIRouter(prefix="/brewery", tags=["Brewery"])

TYPE = "BREWERY"


@router.get("/all")
def read_brewer(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list:
    """
    Reads all brewery instances.
    :param session: DB session.
    :param offset: Start offset.
    :param limit: Maximum query.
    :return: List of all brewery.
    """
    breweries = session.exec(select(Brewery).offset(offset).limit(limit)).all()
    breweries_list = []
    for brewery in breweries:
        brewery_data = brewery.model_dump()
        if brewery.beers:
            brewery_data.update({"beers": brewery.beers})
        else:
            brewery_data.update({"beers": []})
        breweries_list.append(brewery_data)
    return breweries_list


@router.post("/add")
def create_brewery(
    brewery: Brewery, session: Session = Depends(get_session)
) -> Brewery:
    """
    Creates a brewery instance.
    :param brewery: Brewery instance.
    :param session: DB session.
    :return: Created brewery instance.
    """
    if not (brewery.name and brewery.city and brewery.country):
        raise IncompleteException(TYPE)

    session.add(brewery)
    session.commit()
    session.refresh(brewery)
    return brewery


@router.get("/{brewery_id}")
def read_brewery_id(brewery_id: int, session: Session = Depends(get_session)) -> dict:
    """
    Searches for a brewery with id.
    :param brewery_id: ID of a beer to search for.
    :param session: DB session.
    :return: Dictionary with brewery and referenced beer.
    """
    brewery = session.get(Brewery, brewery_id)

    if not brewery:
        raise NotFoundException(TYPE, data_id=brewery_id)

    brewery_json = brewery.model_dump()
    if brewery.beers:
        brewery_json.update({"beers": brewery.beers})

    return brewery_json


@router.get("/name/{brewery_name}")
def read_brewery_name(
    brewery_name: str, session: Session = Depends(get_session)
) -> dict:
    """
    Searches for a brewery with name.
    :param brewery_name: Name of a brewery to search for.
    :param session: DB session.
    :return: Dictionary with brewery and referenced beer.
    """
    statement = select(Brewery).where(Brewery.name == brewery_name)

    try:
        brewery = session.exec(statement).one()
    except Exception as ex:
        raise NotFoundException(TYPE, data_name=brewery_name) from ex

    brewery_json = brewery.model_dump()
    if brewery.beers:
        brewery_json.update({"beers": brewery.beers})

    return brewery_json


@router.delete("/{brewery_id}")
def delete_brewery(
    brewery_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> dict:
    """
    Deletes a brewery with ID.
    :param brewery_id: ID of a brewery to be deleted.
    :param token: User jwt-token.
    :param session: DB session.
    :return: "ok":True if succeeded.
    """
    is_admin(token)

    brewery = session.get(Brewery, brewery_id)

    if not brewery:
        raise NotFoundException(TYPE, data_id=brewery_id)

    session.delete(brewery)
    session.commit()
    return {"ok": True}


@router.patch("/{brewery_id}")
def update_brewery(
    brewery_id: int, brewery: BreweryUpdate, session: Session = Depends(get_session)
) -> type[Brewery]:
    """
    Updates the data of a brewery.
    :param brewery_id: ID of a brewery to be edited.
    :param brewery: Edited brewery data.
    :param session: DB session.
    :return: Edited brewery instance.
    """
    brewery_db = session.get(Brewery, brewery_id)

    if not brewery_db:
        raise NotFoundException(TYPE, data_id=brewery_id)

    brewery_data = brewery.model_dump(exclude_unset=True)
    brewery_db.sqlmodel_update(brewery_data)
    session.commit()
    session.refresh(brewery_db)
    return brewery_db
