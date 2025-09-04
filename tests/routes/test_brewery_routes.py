"""
Created by Fabian Gnatzig
Description: Unittests of brewery routes.
"""

from tests.helper_methods import create_brewery, create_beer


def test_read_empty_brewery(client_fixture):
    """
    Test read brewery without existing.
    :param client_fixture: Test client.
    :return: None
    """
    response = client_fixture.get("/brewery/all")
    assert response.status_code == 200
    assert response.json() == []


def test_read_brewery(client_fixture):
    """
    Test read brewery.
    :param client_fixture: Test client.
    :return: None
    """
    create_brewery(client_fixture)
    create_beer(client_fixture)

    response = client_fixture.get("/brewery/all")
    assert response.status_code == 200
    assert len(response.json()) == 1

    create_brewery(client_fixture)

    response = client_fixture.get("/brewery/all")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_brewery_without_beer(client_fixture):
    """
    Test read brewery without connected brewery.
    :param client_fixture: Test client.
    :return: None
    """
    create_brewery(client_fixture)

    response = client_fixture.get("/brewery/all")
    assert response.status_code == 200
    assert len(response.json()) == 1

    create_brewery(client_fixture)

    response = client_fixture.get("/brewery/all")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_create_brewery(client_fixture):
    """
    Test the brewery creation.
    :param client_fixture: Test client.
    :return: None
    """
    response = create_brewery(client_fixture)
    assert response.status_code == 200
    assert response.json()["name"] == "test_brewery"
    assert response.json()["city"] == "test_city"


def test_create_wrong_brewery(client_fixture):
    """
    Tests the brewery creation exception.
    :param client_fixture: Test client.
    :return: None
    """
    response = client_fixture.post("/brewery/add", json={"no_brewery": "brewery"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Incomplete brewery"


def test_read_brewery_id(client_fixture):
    """
    Test read a brewery with id.
    :param client_fixture: Test client.
    :return: None
    """
    create_brewery(client_fixture)
    create_beer(client_fixture)

    response = client_fixture.get("/brewery/1")
    assert response.status_code == 200
    assert response.json()["name"] == "test_brewery"
    assert response.json()["beers"]


def test_read_wrong_brewery_id(client_fixture):
    """
    Tests the read brewery by id exception.
    :param client_fixture: Test client.
    :return: None
    """
    no_brewery_id = "324234"

    response = client_fixture.get(f"/brewery/{no_brewery_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Brewery with id '{no_brewery_id}' not found!"


def test_read_brewery_name(client_fixture):
    """
    Tests read a brewery by name.
    :param client_fixture: Test client.
    :return: None
    """
    create_brewery(client_fixture)
    create_beer(client_fixture)

    response = client_fixture.get("/brewery/name/test_brewery")
    assert response.json()["name"] == "test_brewery"
    assert response.json()["beers"]


def test_read_wrong_brewery_name(client_fixture):
    """
    Test the read of a brewery by name exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_name = "wrong name"

    response = client_fixture.get(f"/brewery/name/{wrong_name}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Brewery with name '{wrong_name}' not found!"


def test_delete_brewery(client_fixture, get_admin_token):
    """
    Test the deleting of a brewery.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    create_brewery(client_fixture)

    response = client_fixture.delete(
        "/brewery/1", headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_delete_wrong_brewery(client_fixture, get_admin_token):  #
    """
    Test the deletion of a brewery exception.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(
        f"/brewery/{wrong_id}", headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == f"Brewery with id '{wrong_id}' not found!"


def test_delete_brewery_invalid_token(client_fixture, get_invalid_token):
    """
    Test the deletion of a brewery on invalid token exception.
    :param client_fixture: Test client.
    :param get_invalid_token: Test invalid token.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(
        f"/brewery/{wrong_id}", headers={"Authorization": f"Bearer {get_invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token or role"


def test_update_brewery_name(client_fixture):
    """
    Test the update of a brewery.
    :param client_fixture: Test client.
    :return: None
    """
    create_brewery(client_fixture)
    new_name = "new_test_brewery"
    test_payload = {"name": f"{new_name}"}

    response = client_fixture.patch("/brewery/1", json=test_payload)
    assert response.status_code == 200
    assert response.json()["name"] == new_name
    assert response.json()["city"] == "test_city"


def test_update_wrong_brewery(client_fixture):
    """
    Test the update of a brewery exception.
    :param client_fixture: Test client.
    :return: None
    """
    create_brewery(client_fixture)
    wrong_id = 321321
    response = client_fixture.patch(f"/brewery/{wrong_id}", json={})
    assert response.status_code == 404
    assert response.json()["detail"] == f"Brewery with id '{wrong_id}' not found!"
