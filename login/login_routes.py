"""
Created by Fabian Gnatzig
Description: Route and methods for login.
"""
import jwt
from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from dependencies import get_session, SECRET_KEY, ALGORITHM
from login.login_classes import Token
from routes.user.user_routes import get_user_name



router = APIRouter(prefix="/login", tags=["Login"])

def create_access_token(data: dict, expires_delta: timedelta | None = None):
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


def authenticate_user(session: Session, username: str, password: str):
    """
    Authentication of the user and its password.
    :param session: The db session.
    :param username: Username of user that is logging in.
    :param password: Password of user that is logging in.
    :return: User if username and password is valid.
    """
    try:
        #ToDo: Add encryption
        user = get_user_name(username, session)
        if user["password"] == password:
            return user
        return
    except Exception:
        return


def auth_is_user(user_id: int, jwt_token: str):
    """
    Helper method for authenticate if the user access its data.
    :param user_id: ID of user that will be accessed.
    :param jwt_token: JWT-Token of the user that access.
    :return: True if it is the user, False if not.
    """
    decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
    if user_id != decoded_jwt["user_id"]:
        return False
    return True


def auth_is_admin(jwt_token: str):
    """
    Helper method for authenticate the admin.
    :param jwt_token: JWT-Token of the user that access.
    :return: True if it is the user, False if not.
    """
    decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
    if decoded_jwt["role"] != "admin":
        return False
    return True


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
) -> Token:
    """
    Authenticate the user from login.
    :param form_data: Data of the login form.
    :param session: The db session.
    :return: Encoded JWT-Token.
    """
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={
            "username": user["username"],
            "user_id": user["id"],
            "team_ids": user["team"]["id"],
            "role": user["role"]
        },
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

