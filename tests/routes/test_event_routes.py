"""
Created by Fabian Gnatzig
Description: Unittests of event routes.
"""

from tests.helper_methods import (
    create_event,
    create_season,
    create_team,
    create_bring_beer,
)


def test_read_events(client_fixture):
    """
    Test read event.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)
    create_season(client_fixture)
    create_event(client_fixture)

    response = client_fixture.get("/event/all")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_read_event_id(client_fixture):
    """
    Test read event by id.
    :param client_fixture: Test client.
    :return: None
    """
    create_bring_beer(client_fixture)
    create_team(client_fixture)
    create_season(client_fixture)
    create_event(client_fixture)

    response = client_fixture.get("/event/1")
    assert response.status_code == 200
    assert response.json()["name"] == "test_event"
    assert response.json()["season"]
    assert response.json()["bring_beer"]


def test_read_wrong_event_id(client_fixture):
    """
    Test read wrong event by id.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = "324234"

    create_team(client_fixture)
    create_season(client_fixture)
    create_event(client_fixture)

    response = client_fixture.get(f"/event/{wrong_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Event with id '{wrong_id}' not found!"


def test_read_event_name(client_fixture):
    """
    Tests read an event by name.
    :param client_fixture: Test client.
    :return: None
    """
    event_name = "test_event"

    create_bring_beer(client_fixture)
    create_team(client_fixture)
    create_season(client_fixture)
    create_event(client_fixture)

    response = client_fixture.get(f"/event/name/{event_name}")
    assert response.status_code == 200
    assert response.json()["event_date"] == "2025-08-21"
    assert response.json()["season"]
    assert response.json()["bring_beer"]


def test_read_wrong_event_name(client_fixture):
    """
    Test read wrong event by name.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_name = "wrong"

    create_team(client_fixture)
    create_season(client_fixture)
    create_event(client_fixture)

    response = client_fixture.get(f"/event/name/{wrong_name}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Event with name '{wrong_name}' not found!"


def test_add_empty_event(client_fixture):
    """
    Test add an event without name.
    :param client_fixture: Test client.
    :return: None
    """
    test_payload = {
        "name": "",
        "season_id": 1,
        "event_date": "2025-08-21",
    }

    response = client_fixture.post("/event/add", json=test_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid event"


def test_add_event_date_exception(client_fixture):
    """
    Test add an event with wrong date format.
    :param client_fixture: Test client.
    :return: None
    """
    test_payload = {
        "name": "test_event",
        "season_id": 1,
        "event_date": "20-08-2021",
    }

    response = client_fixture.post("/event/add", json=test_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid date"


def test_delete_event(client_fixture, get_admin_token):
    """
    Test the deleting of an event.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    create_team(client_fixture)
    create_season(client_fixture)
    create_event(client_fixture)

    response = client_fixture.delete(
        "/event/1", headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_delete_wrong_event(client_fixture, get_admin_token):  #
    """
    Test the deletion of an event exception.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(
        f"/event/{wrong_id}", headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == f"Event with id '{wrong_id}' not found!"


def test_delete_event_invalid_token(client_fixture, get_invalid_token):
    """
    Test the deletion of an event on invalid token exception.
    :param client_fixture: Test client.
    :param get_invalid_token: Test invalid token.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(
        f"/event/{wrong_id}", headers={"Authorization": f"Bearer {get_invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token or role"


def test_update_event_name(client_fixture):
    """
    Test the update of an event.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)
    create_season(client_fixture)
    create_event(client_fixture)

    new_name = "new_test_event"
    test_payload = {"name": f"{new_name}"}

    response = client_fixture.patch("/event/1", json=test_payload)
    assert response.status_code == 200
    assert response.json()["name"] == new_name
    assert response.json()["season_id"] == 1


def test_update_wrong_event(client_fixture):
    """
    Test the update of an event exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = 321321
    response = client_fixture.patch(f"/event/{wrong_id}", json={})
    assert response.status_code == 404
    assert response.json()["detail"] == f"Event with id '{wrong_id}' not found!"
