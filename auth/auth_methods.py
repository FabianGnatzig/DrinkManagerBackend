"""
Created by Fabian Gnatzig
Description: Methods for authentication.
"""
import jwt

from dependencies import SECRET_KEY, ALGORITHM


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
    :return: True if the user is admin, False if not.
    """
    decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
    if decoded_jwt["role"] != "admin":
        return False
    return True


def auth_is_part_of_team(team_id: int, jwt_token: str):
    """
    Helper method for authenticate the admin.
    :param team_id: ID of team that will be accessed.
    :param jwt_token: JWT-Token of the user that access.
    :return: True if the user is part of the team, False if not.
    """
    decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
    if decoded_jwt["team_id"] != team_id:
        return False
    return True
