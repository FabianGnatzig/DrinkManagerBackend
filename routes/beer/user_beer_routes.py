"""
Created by Fabian Gnatzig
Description: HTTP routes of user beer.
"""

import uuid
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends
from sqlmodel import select, Session

from auth.auth_methods import is_admin, get_team_id
from dependencies import get_session, oauth2_scheme
from exceptions import NotFoundException, InvalidRoleException
from models.beer_models import UserBeer, UserBeerUpdate
from models.user_models import User

router = APIRouter(prefix="/userbeer", tags=["UserBeer"])

TYPE = "USER_BEER"


@router.get("/all")
def read_user_beers(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> Sequence[UserBeer]:
    """
    Reads all user beer instances.
    :param token: User jwt-token.
    :param session: DB session.
    :return: List of all user beers.
    """
    try:
        is_admin(token)
        statement = select(UserBeer)
    except InvalidRoleException:
        team_id = get_team_id(token)
        statement = select(UserBeer).join(User).where(User.team_id == team_id)

    user_beer = session.exec(statement).all()
    return user_beer


@router.post("/add")
def create_user_beer(
    user_beer: UserBeer, session: Session = Depends(get_session)
) -> UserBeer:
    """
    Creates a user beer instance.
    :param user_beer: User beer instance.
    :param session: DB session.
    :return: Created user beer instance.
    """
    if not isinstance(user_beer.user_id, uuid.UUID):
        user_beer.user_id = uuid.UUID(user_beer.user_id)

    user = session.get(User, user_beer.user_id)
    user_beer.user = user if user else None
    session.add(user_beer)
    session.commit()
    session.refresh(user_beer)
    return user_beer


@router.get("/{user_beer_id}")
def read_user_beer_id(
    user_beer_id: uuid.UUID, session: Session = Depends(get_session)
) -> dict:
    """
    Searches for a user beer with beer_id.
    :param user_beer_id: User_beer_id to search for.
    :param session: DB session.
    :return: Dictionary with user beer and referenced user and bring beer.
    """
    user_beer = session.get(UserBeer, user_beer_id)
    if not user_beer:
        raise NotFoundException(TYPE, data_id=user_beer_id)

    user_beer_json = user_beer.model_dump()
    if user_beer.user:
        user_beer_json.update({"user": user_beer.user.model_dump()})
    if user_beer.bring_beer:
        user_beer_json.update({"bring_beer": user_beer.bring_beer.model_dump()})

    return user_beer_json


@router.delete("/{user_beer_id}")
def delete_beer(
    user_beer_id: uuid.UUID,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> dict:
    """
    Deletes a user beer with id.
    :param user_beer_id: ID of a user beer to be deleted.
    :param token: User jwt-token.
    :param session: DB session.
    :return: "ok": True if succeeded.
    """
    is_admin(token)

    user_beer = session.get(UserBeer, user_beer_id)
    if not user_beer:
        raise NotFoundException(TYPE, data_id=user_beer_id)

    session.delete(user_beer)
    session.commit()
    return {"ok": True}


@router.patch("/{user_beer_id}")
def update_beer(
    user_beer_id: uuid.UUID,
    user_beer: UserBeerUpdate,
    session: Session = Depends(get_session),
) -> UserBeer:
    """
    Updates the data of a user beer.
    :param user_beer_id: ID of a user beer to be edited.
    :param user_beer: Edited user beer data.
    :param session: DB session.
    :return: Edited user beer instance.
    """
    user_beer_db = session.get(UserBeer, user_beer_id)
    if not user_beer_db:
        raise NotFoundException(TYPE, data_id=user_beer_id)

    user_beer_data = user_beer.model_dump(exclude_unset=True)
    user_beer_db.sqlmodel_update(user_beer_data)
    session.add(user_beer_db)
    session.commit()
    session.refresh(user_beer_db)
    return user_beer_db
