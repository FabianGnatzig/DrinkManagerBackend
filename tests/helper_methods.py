"""
Created by Fabian Gnatzig

Description: Helper methods for unittests
"""
from fastapi.testclient import TestClient

def create_beer(client: TestClient):
    """
    Creates a test beer.
    :param client: Test client.
    :return: Response from backend.
    """
    test_payload = {
        "name": "test_beer",
        "beer_code": 1234,
        "brewery_id": 1,
        "alcohol": 0.1,
        "volume": 0.2
    }

    response = client.post("/beer/add", json=test_payload)
    return response

def create_brewery(client: TestClient):
    """
    Creates a brewery.
    :param client: Test client.
    :return: Response from backend.
    """
    test_payload = {
        "name": "test_brewery",
        "city": "test_city",
        "country": "test_country"
    }

    response = client.post("/brewery/add", json=test_payload)
    return response


def create_bring_beer(client: TestClient):
    """
    Creates a bring beer.
    :param client: Test client.
    :return: Response from backend.
    """
    test_payload = {
        "beer_id": 1,
        "user_id": 1,
        "user_beer_id": 1,
        "event_id": 1,
    }

    response = client.post("/bringbeer/add", json=test_payload)
    return response


def create_user_beer(client: TestClient):
    """
    Creates a user beer.
    :param client: Test client.
    :return: Response from backend.
    """
    test_payload = {
        "user_id": 1,
        "kind": "test_kind",
    }

    response = client.post("/userbeer/add", json=test_payload)
    return response

def create_user(client: TestClient):
    """
    Creates a user.
    :param client: Test client.
    :return: Response from backend.
    """
    test_payload = {
        "username": "name",
        "first_name": "first",
        "last_name": "last",
        "birthday": "2025-08-21",
        "team_id": 1,
        "password": "pswd",
        "role": "test_role",
    }

    response = client.post("/user/add", json=test_payload)
    return response


def create_event(client: TestClient):
    """
    Creates an event.
    :param client: Test client.
    :return: Response from backend.
    """
    test_payload = {
        "name": "test_event",
        "season_id": 1,
        "event_date": "2025-08-21",
    }

    response = client.post("/event/add", json=test_payload)
    return response


def create_season(client: TestClient):
    """
    Creates a season.
    :param client: Test client.
    :return: Response from backend.
    """
    test_payload = {
        "name": "test_season",
        "team_id": 1,
    }

    response = client.post("/season/add", json=test_payload)
    return response


def create_team(client: TestClient):
    """
    Creates a team.
    :param client: Test client.
    :return: Response from backend.
    """
    test_payload = {
        "name": "test_team"
    }

    response = client.post("/team/add", json=test_payload)
    return response
