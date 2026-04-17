"""
Created by Fabian Gnatzig
Description: Methods for authentication.
"""

import uuid

import jwt

from dependencies import SECRET_KEY, ALGORITHM
from exceptions import InvalidUserException, InvalidTokenException, InvalidRoleException


def is_user(user_id: uuid.UUID, jwt_token: str):
    """
    Helper method for authenticate if the user access its data.
    :param user_id: ID of user that will be accessed.
    :param jwt_token: JWT-Token of the user that access.
    :return: None
    """
    try:
        decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        if user_id != uuid.UUID(decoded_jwt["user_id"]):
            raise InvalidUserException

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as ex:
        raise InvalidTokenException from ex


def is_admin(jwt_token: str):
    """
    Helper method for authenticate the admin.
    :param jwt_token: JWT-Token of the user that access.
    :return: None.
    """
    try:
        decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_jwt["role"] != "admin":
            raise InvalidRoleException

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as ex:
        raise InvalidTokenException from ex


def is_manager(jwt_token: str):
    """
    Helper method for authenticate a manager.
    :param jwt_token: JWT-Token of the user that access.
    :return: None.
    """
    try:
        decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_jwt["role"] != "manager":
            raise InvalidRoleException

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as ex:
        raise InvalidTokenException from ex


def is_user_role(jwt_token: str):
    """
    Helper method for authenticate if it is only a role user.
    :param jwt_token: JWT-Token of the user that access.
    :return: None.
    """
    try:
        decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_jwt["role"] != "user"

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as ex:
        raise InvalidTokenException from ex


def is_user_or_admin(user_id: uuid.UUID, jwt_token: str):
    """
    Helper method for authenticate if the user access its data.
    :param user_id: ID of user that access.
    :param jwt_token: JWT-Token of the user that access.
    :return: None
    """
    try:
        is_admin(jwt_token)
        return
    except InvalidRoleException:
        pass
    except InvalidTokenException as ex:
        raise ex

    is_user(user_id, jwt_token)


def is_admin_or_manager(token: str):
    """
    Helper method for authenticate if the user is admin or manager.
    :param token: JWT-Token of the user that access.
    :return: None
    """
    try:
        is_admin(token)
        return
    except InvalidRoleException:
        pass
    except InvalidTokenException as ex:
        raise ex

    is_manager(token)


def get_team_id(token: str) -> uuid.UUID:
    """
    Helper method for get the team id from the token.
    :param token: JWT-Token of the user that access.
    :return: Team ID of the user.
    """
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return uuid.UUID(decoded_jwt["team_ids"])

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as ex:
        raise InvalidTokenException from ex
