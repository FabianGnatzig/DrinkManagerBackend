"""
Created by Fabian Gnatzig
Description: Unittests of user beer routes.
"""
from tests.helper_methods import create_user_beer, create_user, create_bring_beer


def test_read_empty_user_beers(client_fixture):
    """
    Test read all user_beer.
    :param client_fixture: Test Client.
    :return: None
    """
    response = client_fixture.get("/userbeer/all")
    assert response.status_code == 200
    assert response.json() == []


def test_read_user_beer_id(client_fixture):
    """
    Test read user_beer by id.
    :param client_fixture: Test client.
    :return: None
    """
    create_user(client_fixture)
    create_bring_beer(client_fixture)
    create_user_beer(client_fixture)

    response = client_fixture.get("/userbeer/1")
    assert response.status_code == 200
    assert response.json()["user"]
    assert response.json()["bring_beer"]


def test_read_wrong_user_beer_id(client_fixture):
    """
    Test read user_beer by id exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.get(f"/userbeer/{wrong_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"User beer with id '{wrong_id}' not found!"


def test_delete_user_beer(client_fixture):
    """
    Test the deleting of a user_beer.
    :param client_fixture: Test client.
    :return: None
    """
    create_user(client_fixture)
    create_bring_beer(client_fixture)
    create_user_beer(client_fixture)

    response = client_fixture.delete("/userbeer/1")
    assert response.status_code == 200
    assert response.json()["ok"] == True


def test_delete_wrong_user_beer(client_fixture):  #
    """
    Test the deletion of a user_beer exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(f"/userbeer/{wrong_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"User beer with id '{wrong_id}' not found!"


def test_update_user_beer_name(client_fixture):
    """
    Test the update of a user_beer.
    :param client_fixture: Test client.
    :return: None
    """
    create_user(client_fixture)
    create_bring_beer(client_fixture)
    create_user_beer(client_fixture)
    new_id = 2
    test_payload = {
        "user_id": f"{new_id}"
    }

    response = client_fixture.patch("/userbeer/1", json=test_payload)
    assert response.status_code == 200
    assert response.json()["user_id"] == new_id


def test_update_wrong_user_beer(client_fixture):
    """
    Test the update of a user_beer exception.
    :param client_fixture: Test client.
    :return: None
    """
    create_user(client_fixture)
    create_bring_beer(client_fixture)
    create_user_beer(client_fixture)
    wrong_id = 321321

    response = client_fixture.patch(f"/userbeer/{wrong_id}", json={})
    assert response.status_code == 404
    assert response.json()["detail"] == f"User beer with id '{wrong_id}' not found!"
