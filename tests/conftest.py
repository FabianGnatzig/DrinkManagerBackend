"""
Created by Fabian Gnatzig
Description: Methods and fixtures for unittests.
"""

from datetime import timedelta

import pytest
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient

from auth.login_routes import create_access_token
from dependencies import get_session
from main import app

DATABASE = "sqlite:///test.db"


@pytest.fixture(name="session")
def session_fixture():
    """
    Fixture for creating a test db session.
    """
    test_engine = create_engine(DATABASE)

    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def client_fixture(session: Session):
    """
    Fixture to create a test client.
    :param session: The test db session.
    """

    def get_session_override():
        """
        Method for overriding the production db session with the test db session.
        :return: The test db session.
        """
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def get_admin_token():
    """
    Create an JWT-Token with admin rights.
    :return: Admin JWT-Token.
    """
    token = create_access_token(
        {"sub": "alice", "user_id": 0, "role": "admin"}, timedelta(minutes=12)
    )
    return token


@pytest.fixture
def get_user_token():
    """
    Create an JWT-Token with admin rights.
    :return: Admin JWT-Token.
    """
    token = create_access_token({"sub": "alice", "user_id": 1, "role": "test"})
    return token
