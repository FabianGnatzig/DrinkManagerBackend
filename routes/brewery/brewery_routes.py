"""
Created by Fabian Gnatzig
Description: HTTP routes of brewery's.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from auth.auth_methods import auth_is_admin
from dependencies import get_session, oauth2_scheme
from models.brewery_models import Brewery, BreweryUpdate

router = APIRouter(prefix="/brewery", tags=["Brewery"])


@router.get("/all")
def read_brewer(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list:
    """
    Reads all brewery instances.
    :param session: The db session.
    :param offset: The start offset.
    :param limit: The maximum query.
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
    :param brewery: The brewery instance.
    :param session: The db session.
    :return: The created brewery instance.
    """
    if not (brewery.name and brewery.city and brewery.country):
        raise HTTPException(status_code=400, detail="Incomplete brewery")
    session.add(brewery)
    session.commit()
    session.refresh(brewery)
    return brewery


@router.get("/{brewery_id}")
def read_brewery_id(brewery_id: int, session: Session = Depends(get_session)) -> dict:
    """
    Searches for a brewery with id.
    :param brewery_id: The id of a beer to search for.
    :param session: The db session.
    :return: Dictionary with brewery and referenced beer.
    """
    brewery = session.get(Brewery, brewery_id)

    if not brewery:
        raise HTTPException(
            status_code=404, detail=f"Brewery with id '{brewery_id}' not found!"
        )

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
    :param brewery_name: The name of a brewery to search for.
    :param session: The db session.
    :return: Dictionary with brewery and referenced beer.
    """
    statement = select(Brewery).where(Brewery.name == brewery_name)

    try:
        brewery = session.exec(statement).one()
    except Exception as ex:
        raise HTTPException(
            status_code=404, detail=f"Brewery with name '{brewery_name}' not found!"
        ) from ex

    brewery_json = brewery.model_dump()
    if brewery.beers:
        brewery_json.update({"beers": brewery.beers})

    return brewery_json


@router.delete("/{brewery_id}")
def delete_brewery(
    brewery_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
):
    """
    Deletes a brewery with id.
    :param brewery_id: The id of a brewery to be deleted.
    :param token: User jwt-token.
    :param session: The db session.
    :return: "ok":True if succeeded.
    """
    if not auth_is_admin(token):
        raise HTTPException(status_code=401, detail="Invalid token or role")

    brewery = session.get(Brewery, brewery_id)

    if not brewery:
        raise HTTPException(
            status_code=404, detail=f"Brewery with id '{brewery_id}' not found!"
        )

    session.delete(brewery)
    session.commit()
    return {"ok": True}


@router.patch("/{brewery_id}")
def update_brewery(
    brewery_id: int, brewery: BreweryUpdate, session: Session = Depends(get_session)
):
    """
    Updates the data of a brewery.
    :param brewery_id: The id of a brewery to be edited.
    :param brewery: The edited brewery data.
    :param session: The db session.
    :return: The edited brewery instance.
    """
    brewery_db = session.get(Brewery, brewery_id)

    if not brewery_db:
        raise HTTPException(
            status_code=404, detail=f"Brewery with id '{brewery_id}' not found!"
        )

    brewery_data = brewery.model_dump(exclude_unset=True)
    brewery_db.sqlmodel_update(brewery_data)
    session.add(brewery_db)
    session.commit()
    session.refresh(brewery_db)
    return brewery_db
