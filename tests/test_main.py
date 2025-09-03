"""
Created by Fabian Gnatzig
Description: Test main functions.
"""

from sqlmodel import create_engine, inspect, Session
from dependencies import create_db, get_session, get_json_from_open_ai_response

TABLES = ["beer", "brewery", "bringbeer", "event", "season", "team", "user", "userbeer"]


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


def test_fail_json_from_response():
    """
    Test fails when no json is inside the message.
    :return: None
    """
    data = "Any teststring"
    response = get_json_from_open_ai_response(data)
    assert response["details"] == "No data found!"


def test_json_from_response():
    """
    Test string to json transfer.
    :return: None
    """
    data = 'Any teststring ```json{"key": "data"}```'
    response = get_json_from_open_ai_response(data)
    print(response)
    assert response["key"] == "data"
