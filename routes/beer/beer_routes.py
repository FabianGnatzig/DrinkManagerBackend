"""
Created by Fabian Gnatzig
Description: HTTP routes of beer.
"""

from typing import Annotated

from fastapi import APIRouter, Query, Depends, HTTPException, UploadFile, File
from sqlmodel import select, Session

from auth.auth_methods import is_admin
from dependencies import (
    get_session,
    client,
    OPEN_AI_REQUEST,
    get_json_from_open_ai_response,
    oauth2_scheme,
)
from exceptions import NotFoundException, IncompleteException
from models.beer_models import Beer, BeerUpdate
from models.brewery_models import Brewery

router = APIRouter(prefix="/beer", tags=["Beer"])

TYPE = "BEER"


@router.get("/all")
def read_beers(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list:
    """
    Reads all beer instances.
    :param session: DB session.
    :param offset: Start offset.
    :param limit: Maximum query size.
    :return: List of all beers.
    """
    beers_data = session.exec(select(Beer).offset(offset).limit(limit)).all()
    beers = []
    for beer in beers_data:
        beer_data = beer.model_dump()
        if beer.brewery:
            beer_data.update({"brewery": beer.brewery.model_dump()})
        else:
            beer_data.update({"brewery": {"name": "not found"}})

        if beer.bring_beer:
            beer_data.update({"bring_beer": beer.bring_beer})
        beers.append(beer_data)
    return beers


@router.post("/add")
def create_beer(beer: Beer, session: Session = Depends(get_session)) -> Beer:
    """
    Creates a beer instance.
    :param beer: Beer instance.
    :param session: DB session.
    :return: Created beer instance.
    """
    if not (beer.name and beer.brewery_id and beer.beer_code):
        raise IncompleteException(TYPE)

    session.add(beer)
    session.commit()
    session.refresh(beer)
    return beer


@router.get("/{beer_id}")
def read_beer_id(beer_id: int, session: Session = Depends(get_session)) -> dict:
    """
    Searches for a beer with ID.
    :param beer_id: ID of beer to search for.
    :param session: The db session.
    :return: Dictionary with beer and referenced brewery.
    """
    beer = session.get(Beer, beer_id)
    if not beer:
        raise NotFoundException(TYPE, data_id=beer_id)

    beer_json = beer.model_dump()
    if beer.brewery:
        beer_json.update({"brewery": beer.brewery.model_dump()})
    if beer.bring_beer:
        beer_json.update({"bring_beer": beer.bring_beer})

    return beer_json


@router.get("/code/{beer_code}")
def read_beer_code(beer_code: str, session: Session = Depends(get_session)) -> dict:
    """
    Searches for a beer with beer_code.
    :param beer_code: Beer_code to search for.
    :param session: DB session.
    :return: Dictionary with beer and referenced brewery.
    """
    statement = select(Beer).where(Beer.beer_code == beer_code)
    try:
        beer = session.exec(statement).one()
    except Exception as ex:
        raise NotFoundException(TYPE, data_code=beer_code) from ex

    beer_json = beer.model_dump()
    if beer.brewery:
        beer_json.update({"brewery": beer.brewery.model_dump()})
    if beer.bring_beer:
        beer_json.update({"bring_beer": beer.bring_beer})

    return beer_json


@router.get("/name/{beer_name}")
def read_beer_name(beer_name: str, session: Session = Depends(get_session)) -> dict:
    """
    Searches for a beer with beer_name.
    :param beer_name: Name of a beer to search for.
    :param session: DB session.
    :return: Dictionary with beer and referenced brewery.
    """
    statement = select(Beer).where(Beer.name == beer_name)
    try:
        beer = session.exec(statement).one()
    except Exception as ex:
        raise NotFoundException(TYPE, data_name=beer_name) from ex

    beer_json = beer.model_dump()
    if beer.brewery:
        beer_json.update({"brewery": beer.brewery.model_dump()})
    if beer.bring_beer:
        beer_json.update({"bring_beer": beer.bring_beer})

    return beer_json


@router.delete("/{beer_id}")
def delete_beer(
    beer_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> dict:
    """
    Deletes a beer with ID.
    :param beer_id: ID of a beer to be deleted.
    :param session: DB session.
    :param token: User jwt-token.
    :return: "ok": True if succeeded.
    """
    is_admin(token)

    beer = session.get(Beer, beer_id)
    if not beer:
        raise NotFoundException(TYPE, data_id=beer_id)

    session.delete(beer)
    session.commit()
    return {"ok": True}


@router.patch("/{beer_id}")
def update_beer(
    beer_id: int, beer: BeerUpdate, session: Session = Depends(get_session)
) -> Beer:
    """
    Updates the data of a beer.
    :param beer_id: ID of a beer to be edited.
    :param beer: Edited beer data.
    :param session: DB session.
    :return: Edited beer instance.
    """
    beer_db = session.get(Beer, beer_id)
    if not beer_db:
        raise NotFoundException(TYPE, data_id=beer_id)

    beer_data = beer.model_dump(exclude_unset=True)
    beer_db.sqlmodel_update(beer_data)
    session.commit()
    session.refresh(beer_db)
    return beer_db


@router.post("/upload")
def create_beer_by_image(
    image: UploadFile,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> str | Beer:
    """
    Checks if the beer exists. If not, add the data to the db.
    :param image: File that was uploaded.
    :param token: Authentication token.
    :param session: DB session.
    :return: New created beer data.
    """
    is_admin(token)

    data = get_data_from_open_ai(image)
    if "details" in data.keys():
        raise HTTPException(400, data["details"])

    statement = select(Brewery).where(Brewery.name == data["brewery"])
    try:
        brewery = session.exec(statement).one()
    except Exception as ex:
        raise NotFoundException("BREWERY", data["brewery"]) from ex

    statement = select(Beer).where(Beer.name == data["name"])
    try:
        beer = session.exec(statement).one()
        if beer.brewery.name == brewery.name:
            return (
                f"{TYPE} `{data["name"]}` with code `{data["beer_code"]}` "
                f"from brewery '{brewery.name}' already exists"
            )

    except Exception:
        pass

    data.pop("brewery")
    data["brewery_id"] = brewery.id
    new_beer = Beer(**data)

    session.add(new_beer)
    session.commit()
    session.refresh(new_beer)
    return new_beer


def get_data_from_open_ai(image: File) -> dict:  # pragma: no cover
    """
    Gets the data from a beer label with the help of gpt-4o.
    :param image: Image data of the label.
    :return: Dictionary with beer data.
    """
    file = client.files.create(file=(image.filename, image.file), purpose="user_data")

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "file_id": file.id,
                    },
                    {"type": "input_text", "text": OPEN_AI_REQUEST},
                ],
            }
        ],
        store=True,
    )

    return get_json_from_open_ai_response(response.output_text)
