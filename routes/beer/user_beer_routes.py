"""
Created by Fabian Gnatzig
Description: HTTP routes of user beer.
"""

from typing import Annotated, Sequence

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlmodel import select, Session

from auth.auth_methods import auth_is_admin
from dependencies import get_session, oauth2_scheme
from models.beer_models import UserBeer, UserBeerUpdate
from models.user_models import User

router = APIRouter(prefix="/userbeer", tags=["UserBeer"])


@router.get("/all")
def read_user_beers(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[UserBeer]:
    """
    Reads all user beer instances.
    :param session: The db session.
    :param offset: The start offset.
    :param limit: The maximum query.
    :return: List of all user beers.
    """
    user_beer = session.exec(select(UserBeer).offset(offset).limit(limit)).all()
    return user_beer


@router.post("/add")
def create_user_beer(
    user_beer: UserBeer, session: Session = Depends(get_session)
) -> UserBeer:
    """
    Creates a user beer instance.
    :param user_beer: The user beer instance.
    :param session: The db session.
    :return: The created user beer instance.
    """
    user = session.get(User, user_beer.user_id)
    user_beer.user = user if user else None
    session.add(user_beer)
    session.commit()
    session.refresh(user_beer)
    return user_beer


@router.get("/{user_beer_id}")
def read_user_beer_id(
    user_beer_id: int, session: Session = Depends(get_session)
) -> dict:
    """
    Searches for a user beer with beer_id.
    :param user_beer_id: The user_beer_id to search for.
    :param session: The db session.
    :return: Dictionary with user beer and referenced user and bring beer.
    """
    user_beer = session.get(UserBeer, user_beer_id)
    if not user_beer:
        raise HTTPException(
            status_code=404, detail=f"User beer with id '{user_beer_id}' not found!"
        )

    user_beer_json = user_beer.model_dump()
    if user_beer.user:
        user_beer_json.update({"user": user_beer.user.model_dump()})
    if user_beer.bring_beer:
        user_beer_json.update({"bring_beer": user_beer.bring_beer.model_dump()})

    return user_beer_json


@router.delete("/{user_beer_id}")
def delete_beer(
    user_beer_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
):
    """
    Deletes a user beer with id.
    :param user_beer_id: ID of a user beer to be deleted.
    :param token: User jwt-token.
    :param session: DB session.
    :return: "ok": True if succeeded.
    """
    if not auth_is_admin(token):
        raise HTTPException(status_code=401, detail="Invalid token or role")

    user_beer = session.get(UserBeer, user_beer_id)
    if not user_beer:
        raise HTTPException(
            status_code=404, detail=f"User beer with id '{user_beer_id}' not found!"
        )

    session.delete(user_beer)
    session.commit()
    return {"ok": True}


@router.patch("/{user_beer_id}")
def update_beer(
    user_beer_id: int,
    user_beer: UserBeerUpdate,
    session: Session = Depends(get_session),
):
    """
    Updates the data of a user beer.
    :param user_beer_id: The id of a user beer to be edited.
    :param user_beer: The edited user beer data.
    :param session: The db session.
    :return: The edited user beer instance.
    """
    user_beer_db = session.get(UserBeer, user_beer_id)
    if not user_beer_db:
        raise HTTPException(
            status_code=404, detail=f"User beer with id '{user_beer_id}' not found!"
        )

    user_beer_data = user_beer.model_dump(exclude_unset=True)
    user_beer_db.sqlmodel_update(user_beer_data)
    session.add(user_beer_db)
    session.commit()
    session.refresh(user_beer_db)
    return user_beer_db
