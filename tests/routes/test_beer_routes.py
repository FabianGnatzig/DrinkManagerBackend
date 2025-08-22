"""
Created by Fabian Gnatzig
Description: Unittests of beer-routes.
"""
from tests.helper_methods import create_brewery, create_bring_beer, create_beer


def test_read_empty_beers(client_fixture):
    """
    Test read beer without existing.
    :param client_fixture: Test client.
    :return: None
    """
    response = client_fixture.get("/beer/all")
    assert response.status_code == 200
    assert response.json() == []


def test_read_beers(client_fixture):
    """
    Test read beer.
    :param client_fixture: Test client.
    :return: None
    """
    create_brewery(client_fixture)
    create_bring_beer(client_fixture)
    create_beer(client_fixture)

    response = client_fixture.get("/beer/all")
    assert response.status_code == 200
    assert len(response.json()) == 1

    create_beer(client_fixture)

    response = client_fixture.get("/beer/all")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_read_beer_without_brewery(client_fixture):
    """
    Test read beer without connected brewery.
    :param client_fixture: Test client.
    :return: None
    """
    create_beer(client_fixture)

    response = client_fixture.get("/beer/all")
    assert response.status_code == 200
    assert len(response.json()) == 1

    create_beer(client_fixture)

    response = client_fixture.get("/beer/all")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_create_beer(client_fixture):
    """
    Test the beer creation.
    :param client_fixture: Test client.
    :return: None
    """
    response = create_beer(client_fixture)
    assert response.status_code == 200
    assert response.json()["beer_code"] == 1234
    assert response.json()["volume"] == 0.2
    assert response.json()["id"] == 1

def test_create_wrong_beer(client_fixture):
    """
    Tests the creation exception.
    :param client_fixture: Test client.
    :return: None
    """
    response = client_fixture.post("/beer/add", json={"no_beer": "beer"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Incomplete beer"


def test_read_beer_id(client_fixture):
    """
    Test read a beer with id.
    :param client_fixture: Test client.
    :return: None
    """
    create_brewery(client_fixture)
    create_bring_beer(client_fixture)
    create_beer(client_fixture)

    response = client_fixture.get("/beer/1")
    assert response.status_code == 200
    assert response.json()["beer_code"] == 1234
    assert response.json()["volume"] == 0.2


def test_read_wrong_beer_id(client_fixture):
    """
    Tests the read beer by id exception.
    :param client_fixture: Test client.
    :return: None
    """
    no_beer_id = "324234"

    response = client_fixture.get(f"/beer/{no_beer_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Beer with id '{no_beer_id}' not found!"


def test_read_beer_name(client_fixture):
    """
    Tests read a beer by name.
    :param client_fixture: Test client.
    :return: None
    """
    create_brewery(client_fixture)
    create_bring_beer(client_fixture)
    create_beer(client_fixture)

    response = client_fixture.get("/beer/name/test_beer")
    assert response.json()["beer_code"] == 1234
    assert response.json()["volume"] == 0.2


def test_read_wrong_beer_name(client_fixture):
    """
    Test the read of a beer by name exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_name = "wrong name"

    response = client_fixture.get(f"/beer/name/{wrong_name}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Beer with name '{wrong_name}' not found!"

def test_delete_beer(client_fixture):
    """
    Test the deleting of a beer.
    :param client_fixture: Test client.
    :return: None
    """
    create_beer(client_fixture)

    response = client_fixture.delete("/beer/1")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_delete_wrong_beer(client_fixture):#
    """
    Test the deletion of a beer exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(f"/beer/{wrong_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Beer with id '{wrong_id}' not found!"


def test_update_beer_name(client_fixture):
    """
    Test the update of a beer.
    :param client_fixture: Test client.
    :return: None
    """
    create_beer(client_fixture)
    new_name = "new_test_beer"
    test_payload = {
        "name": f"{new_name}"
    }

    response = client_fixture.patch("/beer/1", json=test_payload)
    assert response.status_code == 200
    assert response.json()["name"] == new_name
    assert response.json()["beer_code"] == 1234
    assert response.json()["volume"] == 0.2


def test_update_wrong_beer(client_fixture):
    """
    Test the update of a beer exception.
    :param client_fixture: Test client.
    :return: None
    """
    create_beer(client_fixture)
    wrong_id = 321321
    response = client_fixture.patch(f"/beer/{wrong_id}", json={})
    assert response.status_code == 404
    assert response.json()["detail"] == f"Beer with id '{wrong_id}' not found!"
