"""
Created by Fabian Gnatzig

Description: 
"""
import os

import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

from dependencies import get_session, create_db
from main import app

DATABASE = "sqlite:///test.db"


@pytest.fixture(name="session")
def session_fixture(monkeypatch):
    """
    Fixture for creating a test db session.
    """
    os.environ["DATABASE"] = DATABASE
    test_engine = create_engine(DATABASE)
    monkeypatch.setattr("dependencies.engine", test_engine)

    create_db()

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
