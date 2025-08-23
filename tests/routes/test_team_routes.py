"""
Created by Fabian Gnatzig
Description: Unittests for team routes.
"""

from tests.helper_methods import create_team, create_season, create_user


def test_read_team(client_fixture):
    """
    Test read team.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)

    response = client_fixture.get("/team/all")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_read_team_id(client_fixture):
    """
    Test read team by id.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)
    create_season(client_fixture)
    create_user(client_fixture)

    response = client_fixture.get("/team/1")
    assert response.status_code == 200
    assert response.json()["name"] == "test_team"
    assert response.json()["users"]
    assert response.json()["seasons"]


def test_read_wrong_team_id(client_fixture):
    """
    Test read wrong team by id.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = "324234"

    create_team(client_fixture)

    response = client_fixture.get(f"/team/{wrong_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Team with id '{wrong_id}' not found!"


def test_read_team_name(client_fixture):
    """
    Tests read a team by name.
    :param client_fixture: Test client.
    :return: None
    """
    team_name = "test_team"
    create_team(client_fixture)
    create_season(client_fixture)
    create_user(client_fixture)

    response = client_fixture.get(f"/team/name/{team_name}")
    assert response.status_code == 200
    assert response.json()["name"] == "test_team"
    assert response.json()["users"]
    assert response.json()["seasons"]


def test_read_wrong_team_name(client_fixture):
    """
    Test read wrong team by name.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_name = "wrong"

    create_team(client_fixture)

    response = client_fixture.get(f"/team/name/{wrong_name}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Team with name '{wrong_name}' not found!"


def test_delete_team(client_fixture):
    """
    Test the deleting of a team.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)

    response = client_fixture.delete("/team/1")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_delete_wrong_team(client_fixture):  #
    """
    Test the deletion of a team exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(f"/team/{wrong_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Team with id '{wrong_id}' not found!"


def test_update_team_name(client_fixture):
    """
    Test the update of a team.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)

    new_name = "new_test_team"
    test_payload = {"name": f"{new_name}"}

    response = client_fixture.patch("/team/1", json=test_payload)
    assert response.status_code == 200
    assert response.json()["name"] == new_name


def test_add_wrong_team_name(client_fixture):
    """
    Test the creation of a team with wrong name.
    :param client_fixture: Test client.
    :return: None
    """
    create_team(client_fixture)

    test_payload = {"name": ""}

    response = client_fixture.post("/team/add", json=test_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Incomplete team"


def test_update_wrong_team(client_fixture):
    """
    Test the update of a team exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = 321321
    response = client_fixture.patch(f"/team/{wrong_id}", json={})
    assert response.status_code == 404
    assert response.json()["detail"] == f"Team with id '{wrong_id}' not found!"
