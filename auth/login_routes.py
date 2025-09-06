"""
Created by Fabian Gnatzig
Description: Route and methods for auth.
"""

from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from dependencies import get_session, SECRET_KEY, ALGORITHM, pwd_context
from auth.login_classes import Token
from routes.user.user_routes import get_user_name


router = APIRouter(prefix="/auth", tags=["Authentication"])


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Creates an JWT-Token with data.
    :param data: Data that should be included to the token.
    :param expires_delta: Delta of time that the token should be valid.
    :return: JWT-Token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(session: Session, username: str, password: str) -> dict:
    """
    Authentication of the user and its password.
    :param session: The db session.
    :param username: Username of user that is logging in.
    :param password: Password of user that is logging in.
    :return: User if username and password is valid.
    """
    exception = HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = get_user_name(username, session)
        if pwd_context.verify(password, user["password"]):
            return user

    except HTTPException as ex:
        raise exception from ex

    raise exception


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
) -> Token:
    """
    Authenticate the user from auth.
    :param form_data: Data of the auth form.
    :param session: The db session.
    :return: Encoded JWT-Token.
    """
    user = authenticate_user(session, form_data.username, form_data.password)

    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={
            "username": user["username"],
            "user_id": user["id"],
            "team_ids": user["team"]["id"],
            "role": user["role"],
        },
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
