"""
Created by Fabian Gnatzig
Description: Methods for authentication.
"""

import jwt

from dependencies import SECRET_KEY, ALGORITHM
from exceptions import InvalidUserException, InvalidTokenException, InvalidRoleException


def auth_is_user(user_id: int, jwt_token: str):
    """
    Helper method for authenticate if the user access its data.
    :param user_id: ID of user that will be accessed.
    :param jwt_token: JWT-Token of the user that access.
    :return: True if it is the user, False if not.
    """
    try:
        decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        if user_id != decoded_jwt["user_id"]:
            raise InvalidUserException

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise InvalidTokenException


def auth_is_admin(jwt_token: str):
    """
    Helper method for authenticate the admin.
    :param jwt_token: JWT-Token of the user that access.
    :return: True if the user is admin, False if not.
    """
    try:
        decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_jwt["role"] != "admin":
            raise InvalidRoleException

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise InvalidTokenException


def auth_is_user_or_admin(user_id: int, jwt_token: str):
    """
    Helper method for authenticate if the user access its data.
    :param user_id: ID of user that access.
    :param jwt_token: JWT-Token of the user that access.
    :return: None
    """
    try:
        auth_is_admin(jwt_token)
        return
    except InvalidRoleException:
        pass
    except InvalidTokenException as ex:
        raise ex

    auth_is_user(user_id, jwt_token)
