"""
Created by Fabian Gnatzig
Description:
"""
import os
from sqlmodel import create_engine, inspect, Session
from dependencies import create_db, get_session

TABLES = ['beer', 'brewery', 'bringbeer', 'event', 'season', 'team', 'user', 'userbeer']

def test_root(client_fixture):
    """
    Tests the root route.
    :param client_fixture: Test client.
    :return: None
    """
    response = client_fixture.get("/")
    assert response.status_code == 200


def test_create_db(monkeypatch):
    """
    Test the creation of a DB.
    :param monkeypatch: Monkeypatch fixture.
    :return: None
    """
    test_engine = create_engine("sqlite:///test.db")
    monkeypatch.setattr("dependencies.engine", test_engine)
    create_db()
    inspector = inspect(test_engine)
    test_tables = inspector.get_table_names()

    for table in TABLES:
        assert table in test_tables


def test_get_session(monkeypatch):
    """
    Test the creation of a session.
    :param monkeypatch: Monkeypatch fixture.
    :return: None
    """
    test_engine = create_engine("sqlite:///test.db")
    monkeypatch.setattr("dependencies.engine", test_engine)
    session_gen = get_session()
    test_session = next(session_gen)

    assert isinstance(test_session, Session)

    session_gen.close()
