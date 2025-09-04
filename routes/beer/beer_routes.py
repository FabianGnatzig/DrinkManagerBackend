"""
Created by Fabian Gnatzig
Description: HTTP routes of beer.
"""

from typing import Annotated

from fastapi import APIRouter, Query, Depends, HTTPException, UploadFile, File
from sqlmodel import select, Session

from auth.auth_methods import auth_is_admin
from dependencies import (
    get_session,
    client,
    OPEN_AI_REQUEST,
    get_json_from_open_ai_response,
    oauth2_scheme,
)
from models.beer_models import Beer, BeerUpdate
from models.brewery_models import Brewery

router = APIRouter(prefix="/beer", tags=["Beer"])


@router.get("/all")
def read_beers(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list:
    """
    Reads all beer instances.
    :param session: The db session.
    :param offset: The start offset.
    :param limit: The maximum query.
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
    :param beer: The beer instance.
    :param session: The db session.
    :return: The created beer instance.
    """
    if not (beer.name and beer.brewery_id and beer.beer_code):
        raise HTTPException(status_code=400, detail="Incomplete beer")
    session.add(beer)
    session.commit()
    session.refresh(beer)
    return beer


@router.get("/{beer_id}")
def read_beer_id(beer_id: int, session: Session = Depends(get_session)) -> dict:
    """
    Searches for a beer with beer_id.
    :param beer_id: The beer_id to search for.
    :param session: The db session.
    :return: Dictionary with beer and referenced brewery.
    """
    beer = session.get(Beer, beer_id)
    if not beer:
        raise HTTPException(
            status_code=404, detail=f"Beer with id '{beer_id}' not found!"
        )

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
    :param beer_code: The beer_code to search for.
    :param session: The db session.
    :return: Dictionary with beer and referenced brewery.
    """
    statement = select(Beer).where(Beer.beer_code == beer_code)
    try:
        beer = session.exec(statement).one()
    except Exception as ex:
        raise HTTPException(
            status_code=404, detail=f"Beer with code '{beer_code}' not found!"
        ) from ex

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
    :param beer_name: The name of a beer to search for.
    :param session: The db session.
    :return: Dictionary with beer and referenced brewery.
    """
    statement = select(Beer).where(Beer.name == beer_name)
    try:
        beer = session.exec(statement).one()
    except Exception as ex:
        raise HTTPException(
            status_code=404, detail=f"Beer with name '{beer_name}' not found!"
        ) from ex

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
):
    """
    Deletes a beer with id.
    :param beer_id: The id of a beer to be deleted.
    :param session: The db session.
    :param token: User jwt-token.
    :return: "ok": True if succeeded.
    """
    if not auth_is_admin(token):
        raise HTTPException(status_code=401, detail="Invalid token or role")

    beer = session.get(Beer, beer_id)
    if not beer:
        raise HTTPException(
            status_code=404, detail=f"Beer with id '{beer_id}' not found!"
        )

    session.delete(beer)
    session.commit()
    return {"ok": True}


@router.patch("/{beer_id}")
def update_beer(
    beer_id: int, beer: BeerUpdate, session: Session = Depends(get_session)
):
    """
    Updates the data of a beer.
    :param beer_id: The id of a beer to be edited.
    :param beer: The edited beer data.
    :param session: The db session.
    :return: The edited beer instance.
    """
    beer_db = session.get(Beer, beer_id)
    if not beer_db:
        raise HTTPException(
            status_code=404, detail=f"Beer with id '{beer_id}' not found!"
        )

    beer_data = beer.model_dump(exclude_unset=True)
    beer_db.sqlmodel_update(beer_data)
    session.add(beer_db)
    session.commit()
    session.refresh(beer_db)
    return beer_db


@router.post("/upload")
def create_beer_by_image(
    image: UploadFile,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
):  # pragma: no cover
    """
    Checks if the beer exists. If not, add the data to the db.
    :param image: File that was uploaded.
    :param token: Authentication token.
    :param session: DB session.
    :return: New created beer data.
    """
    # ToDo: Create unittest
    if not auth_is_admin(token):
        raise HTTPException(status_code=401, detail="Invalid token or role")

    if not image:
        raise HTTPException(status_code=400, detail="No image")

    data = get_data_from_open_ai(image)
    if "details" in data.keys():
        raise HTTPException(400, data["details"])

    statement = select(Brewery).where(Brewery.name == data["brewery"])
    try:
        brewery = session.exec(statement).one()
    except Exception as ex:
        raise HTTPException(
            status_code=404,
            detail=f"Brewery with name '{data["brewery"]}' not found!",
        ) from ex

    statement = select(Beer).where(Beer.name == data["name"])
    try:
        beer = session.exec(statement).one()
        if beer.brewery.name == brewery.name:
            return (
                f"Beer `{data["name"]}` with code `{data["beer_code"]}` "
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

    return HTTPException(400, "No image was uploaded")


def get_data_from_open_ai(image: File):  # pragma: no cover
    """
    Gets the data from a beer label with the help of gpt-4o.
    :param image: Image data of the label.
    :return: None
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
