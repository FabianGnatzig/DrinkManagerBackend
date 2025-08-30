"""
Created by Fabian Gnatzig
Description: Unittest for authentication.
"""

from fastapi import HTTPException

import pytest
from sqlmodel import Session

from auth.login_routes import authenticate_user
from tests.helper_methods import create_user, create_team


def test_authenticate_user(session: Session, client_fixture):
    """
    Test the authentication of a user.
    :param session: Test session.
    :param client_fixture: Test client.
    :return: None
    """

    create_user(client_fixture)
    user = authenticate_user(session, "name", "pswd")
    assert user["first_name"] == "first"
    assert user["role"] == "test_role"


def test_authenticate_wrong_password(session: Session, client_fixture):
    """
    Test the failure of authentication of a user.
    :param session: Test session.
    :param client_fixture: Test client.
    :return: None
    """

    create_user(client_fixture)

    with pytest.raises(HTTPException) as info:
        authenticate_user(session, "name", "wrong")

    assert info.value.status_code == 401


def test_authenticate_wrong_user(session: Session, client_fixture):
    """
    Test the failure of authentication of a not existing user.
    :param session: Test session.
    :param client_fixture: Test client.
    :return: None
    """

    create_user(client_fixture)
    with pytest.raises(HTTPException):
        authenticate_user(session, "wrong", "wrong")


def test_login_success(client_fixture):
    """
    Test the successful login.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)
    create_user(client_fixture)

    response = client_fixture.post(
        "/auth/token",
        data={"username": "name", "password": "pswd"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_invalid_password(client_fixture):
    """
    Tests the login with an invalid password.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)
    create_user(client_fixture)

    response = client_fixture.post(
        "/auth/token",
        data={"username": "name", "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_nonexistent_user(client_fixture):
    """
    Tests the login with a non exiting user.
    :param client_fixture: Test client.
    :return: None
    """
    response = client_fixture.post(
        "/token",
        data={"username": "ghost", "password": "doesntmatter"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 404
