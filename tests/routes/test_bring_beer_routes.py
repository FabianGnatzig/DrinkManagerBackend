"""
Created by Fabian Gnatzig
Description: Unittests of bring beer routes.
"""

from tests.helper_methods import (
    create_bring_beer,
    create_beer,
    create_event,
    create_user,
)


def test_read_empty_bring_beers(client_fixture):
    """
    Test read all bring_beer.
    :param client_fixture: Test Client.
    :return: None
    """
    response = client_fixture.get("/bringbeer/all")
    assert response.status_code == 200
    assert response.json() == []


def test_read_bring_beer_id(client_fixture, get_admin_token):
    """
    Test read bring_beer by id.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    create_bring_beer(client_fixture)
    create_beer(client_fixture)
    create_user(client_fixture, get_admin_token)
    create_event(client_fixture)

    response = client_fixture.get("/bringbeer/1")
    assert response.status_code == 200
    assert response.json()["user"]
    assert response.json()["event"]
    assert response.json()["beer"]


def test_read_wrong_bring_beer_id(client_fixture):
    """
    Test read bring_beer by id exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.get(f"/bringbeer/{wrong_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"BRING_BEER with id '{wrong_id}' not found!"


def test_delete_bring_beer(client_fixture, get_admin_token):
    """
    Test the deleting of a bring_beer.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    create_bring_beer(client_fixture)

    response = client_fixture.delete(
        "/bringbeer/1", headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_delete_wrong_bring_beer(client_fixture, get_admin_token):  #
    """
    Test the deletion of a bring_beer exception.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(
        f"/bringbeer/{wrong_id}", headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == f"BRING_BEER with id '{wrong_id}' not found!"


def test_delete_bring_beer_invalid_token(client_fixture, get_invalid_token):
    """
    Test the deletion of a bring_beer on invalid token exception.
    :param client_fixture: Test client.
    :param get_invalid_token: Test invalid token.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(
        f"/bringbeer/{wrong_id}",
        headers={"Authorization": f"Bearer {get_invalid_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_update_bring_beer_name(client_fixture):
    """
    Test the update of a bring_beer.
    :param client_fixture: Test client.
    :return: None
    """
    create_bring_beer(client_fixture)
    new_id = 2
    test_payload = {"beer_id": f"{new_id}"}

    response = client_fixture.patch("/bringbeer/1", json=test_payload)
    assert response.status_code == 200
    assert response.json()["beer_id"] == new_id


def test_update_wrong_bring_beer(client_fixture):
    """
    Test the update of a bring_beer exception.
    :param client_fixture: Test client.
    :return: None
    """
    create_bring_beer(client_fixture)
    wrong_id = 321321

    response = client_fixture.patch(f"/bringbeer/{wrong_id}", json={})
    assert response.status_code == 404
    assert response.json()["detail"] == f"BRING_BEER with id '{wrong_id}' not found!"


def test_read_done_bring_beer(client_fixture):
    """
    Test do and read a bring_beer.
    :param client_fixture: Test client.
    :return: None
    """
    create_bring_beer(client_fixture)
    client_fixture.get("/bringbeer/done/1")

    response = client_fixture.get("/bringbeer/1")
    assert response.status_code == 200
    assert response.json()["done"]
