"""
Created by Fabian Gnatzig
Description: Unittests of season routes.
"""
from tests.helper_methods import create_season, create_team, create_event


def test_read_season(client_fixture):
    """
    Test read season.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)
    create_season(client_fixture)

    response = client_fixture.get("/season/all")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_read_season_id(client_fixture):
    """
    Test read season by id.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)
    create_season(client_fixture)
    create_event(client_fixture)

    response = client_fixture.get("/season/1")
    assert response.status_code == 200
    assert response.json()["name"] == "test_season"


def test_read_wrong_season_id(client_fixture):
    """
    Test read wrong season by id.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = "324234"

    create_team(client_fixture)
    create_season(client_fixture)

    response = client_fixture.get(f"/season/{wrong_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Season with id '{wrong_id}' not found!"


def test_read_season_name(client_fixture):
    """
    Tests read a season by name.
    :param client_fixture: Test client.
    :return: None
    """
    event_name = "test_season"

    create_team(client_fixture)
    create_season(client_fixture)
    create_event(client_fixture)

    response = client_fixture.get(f"/season/name/{event_name}")
    assert response.status_code == 200
    assert response.json()["team_id"] == 1


def test_read_wrong_season_name(client_fixture):
    """
    Test read wrong season by name.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_name = "wrong"

    create_team(client_fixture)
    create_season(client_fixture)

    response = client_fixture.get(f"/season/name/{wrong_name}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Season with name '{wrong_name}' not found!"

def test_add_empty_season(client_fixture):
    """
    Test add a season without name.
    :param client_fixture: Test client.
    :return: None
    """
    test_payload = {
        "name": "",
        "team_id": 1,
    }

    response = client_fixture.post("/season/add", json=test_payload)
    assert response.status_code== 400
    assert response.json()["detail"] == "Invalid season"


def test_add_season_without_team(client_fixture):
    """
    Test add a season with wrong team id.
    :param client_fixture: Test client.
    :return: None
    """
    test_payload = {
        "name": "",
        "team_id": 1,
    }

    response = client_fixture.post("/season/add", json=test_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid season"


def test_delete_season(client_fixture):
    """
    Test the deleting of a season.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)
    create_season(client_fixture)

    response = client_fixture.delete("/season/1")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_delete_wrong_season(client_fixture):#
    """
    Test the deletion of a season exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(f"/season/{wrong_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Season with id '{wrong_id}' not found!"


def test_update_season_name(client_fixture):
    """
    Test the update of a season.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)
    create_season(client_fixture)

    new_name = "new_test_season"
    test_payload = {
        "name": f"{new_name}"
    }

    response = client_fixture.patch("/season/1", json=test_payload)
    assert response.status_code == 200
    assert response.json()["name"] == new_name
    assert response.json()["team_id"] == 1


def test_update_wrong_season(client_fixture):
    """
    Test the update of a season exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = 321321
    response = client_fixture.patch(f"/season/{wrong_id}", json={})
    assert response.status_code == 404
    assert response.json()["detail"] == f"Season with id '{wrong_id}' not found!"
