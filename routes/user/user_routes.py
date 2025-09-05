"""
Created by Fabian Gnatzig
Description: HTTP Routes of user.
"""

from datetime import datetime
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from dependencies import get_session, oauth2_scheme, pwd_context
from auth.auth_methods import auth_is_admin, auth_is_user_or_admin
from exceptions import (
    InvalidException,
    NotFoundException,
)
from models.user_models import User, UserUpdate

router = APIRouter(prefix="/user", tags=["User"])
TYPE = "USER"


@router.get("/all")
def get_all_user(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[User]:
    """
    Reads all user instances.
    :param session: The db session.
    :param offset: The start offset.
    :param limit: The maximum query.
    :return: List of all users.
    """
    statement = select(User).offset(offset).limit(limit)
    users = session.exec(statement).all()
    return users


@router.post("/add")
def create_user(user_data: dict, session: Session = Depends(get_session)) -> User:
    """
    Creates a user instance.
    :param user_data: The user data.
    :param session: The db session.
    :return: The created user instance.
    """
    try:
        user_data["birthday"] = datetime.strptime(
            user_data["birthday"], "%Y-%m-%d"
        ).date()
    except Exception as ex:
        raise InvalidException("birthday") from ex

    user_data["password"] = pwd_context.hash(user_data["password"])

    user = User(**user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/{user_id}")
def get_user_id(
    user_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> dict:
    """
    Searches for a user with id.
    :param user_id: The id of a user to search for.
    :param token: Authentication token.
    :param session: The db session.
    :return: Dictionary with user and team.
    """
    user = session.get(User, user_id)

    if not user:
        raise NotFoundException(TYPE, data_id=user_id)

    auth_is_user_or_admin(user_id, token)

    user_json = user.model_dump()
    if user.team:
        user_json.update({"team": user.team.model_dump()})
    if user.bring_beer:
        user_json.update({"bring_beer": user.bring_beer})
    if user.user_beer:
        user_json.update({"user_beer": user.user_beer})
    return user_json


@router.get("/name/{user_name}")
def get_user_name(user_name: str, session: Session = Depends(get_session)) -> dict:
    """
    Searches for a user with last name.
    :param user_name: The username of a user to search for.
    :param session: The db session.
    :return: Dictionary with user and team.
    """
    statement = select(User).where(User.username == user_name)
    try:
        user = session.exec(statement).one()
    except Exception as ex:
        raise NotFoundException(TYPE, data_name=user_name) from ex

    user_json = user.model_dump()
    if user.team:
        user_json.update({"team": user.team.model_dump()})
    if user.bring_beer:
        user_json.update({"bring_beer": user.bring_beer})
    if user.user_beer:
        user_json.update({"user_beer": user.user_beer})
    return user_json


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> dict:
    """
    Deletes a user with id.
    :param user_id: The id of a user to be deleted.
    :param token: User jwt-token.
    :param session: The db session.
    :return: "ok": True if succeeded.
    """
    auth_is_admin(token)

    user = session.get(User, user_id)
    if not user:
        raise NotFoundException(TYPE, data_id=user_id)

    session.delete(user)
    session.commit()
    return {"ok": True}


@router.patch("/{user_id}")
def update_user(
    user_id: int, user: UserUpdate, session: Session = Depends(get_session)
) -> User:
    """
    Updates the data of a user.
    :param user_id: The id of a user to be edited.
    :param user: The edited user data.
    :param session: The db session.
    :return: The edited user instance.
    """
    user_db = session.get(User, user_id)
    if not user_db:
        raise NotFoundException(TYPE, data_id=user_id)

    user_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db
