"""
Created by Fabian Gnatzig
Description: Unittests of beer-routes.
"""

from unittest.mock import patch

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
    assert response.json()["beer_code"] == "1234"
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
    assert response.json()["detail"] == "Incomplete BEER"


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
    assert response.json()["beer_code"] == "1234"
    assert response.json()["volume"] == 0.2
    assert response.json()["brewery"]
    assert response.json()["bring_beer"]


def test_read_wrong_beer_id(client_fixture):
    """
    Tests the read beer by id exception.
    :param client_fixture: Test client.
    :return: None
    """
    no_beer_id = "324234"

    response = client_fixture.get(f"/beer/{no_beer_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"BEER with id '{no_beer_id}' not found!"


def test_read_beer_by_code(client_fixture):
    """
    Test the read beer by code.
    :param client_fixture: Test client.
    :return: None
    """
    create_brewery(client_fixture)
    create_beer(client_fixture)
    create_bring_beer(client_fixture)
    response = client_fixture.get("/beer/code/1234")
    assert response.status_code == 200
    assert response.json()["beer_code"] == "1234"
    assert response.json()["volume"] == 0.2
    assert response.json()["brewery"]
    assert response.json()["bring_beer"]


def test_fail_read_beer_by_code(client_fixture):
    """
    Test the fail of read beer by code.
    :param client_fixture: Test client.
    :return: None
    """
    response = client_fixture.get("/beer/code/nope")
    assert response.status_code == 404
    assert response.json()["detail"] == "BEER with code 'nope' not found!"


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
    assert response.json()["beer_code"] == "1234"
    assert response.json()["volume"] == 0.2
    assert response.json()["brewery"]
    assert response.json()["bring_beer"]


def test_read_wrong_beer_name(client_fixture):
    """
    Test the read of a beer by name exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_name = "wrong name"

    response = client_fixture.get(f"/beer/name/{wrong_name}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"BEER with name '{wrong_name}' not found!"


def test_delete_beer(client_fixture, get_admin_token):
    """
    Test the deleting of a beer.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    create_beer(client_fixture)

    response = client_fixture.delete(
        "/beer/1", headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_delete_wrong_beer(client_fixture, get_admin_token):  #
    """
    Test the deletion of a beer exception.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(
        f"/beer/{wrong_id}", headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == f"BEER with id '{wrong_id}' not found!"


def test_delete_beer_invalid_token(client_fixture, get_invalid_token):
    """
    Test the deletion of a beer on invalid token exception.
    :param client_fixture: Test client.
    :param get_invalid_token: Test invalid token.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(
        f"/beer/{wrong_id}", headers={"Authorization": f"Bearer {get_invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_update_beer_name(client_fixture):
    """
    Test the update of a beer.
    :param client_fixture: Test client.
    :return: None
    """
    create_beer(client_fixture)
    new_name = "new_test_beer"
    test_payload = {"name": f"{new_name}"}

    response = client_fixture.patch("/beer/1", json=test_payload)
    assert response.status_code == 200
    assert response.json()["name"] == new_name
    assert response.json()["beer_code"] == "1234"
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
    assert response.json()["detail"] == f"BEER with id '{wrong_id}' not found!"


def test_create_beer_by_image(tmp_path, client_fixture, get_admin_token):
    """
    Test the creation of a beer by image.
    :param tmp_path: Test path of image.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    create_brewery(client_fixture)
    file_path = tmp_path / "test.png"
    file_path.write_bytes(b"fake image content")

    fake_data = {
        "name": "Test Beer",
        "beer_code": "TB001",
        "brewery": "test_brewery",
        "alcohol": 5.0,
        "volume": 0.2,
    }

    with patch("routes.beer.beer_routes.get_data_from_open_ai", return_value=fake_data):
        response = client_fixture.post(
            "/beer/upload",
            headers={"Authorization": f"Bearer {get_admin_token}"},
            files={"image": ("test.png", file_path.read_bytes(), "image/png")},
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Test Beer"
    assert response.json()["beer_code"] == "TB001"


def test_create_beer_without_brewery_by_image(
    tmp_path, client_fixture, get_admin_token
):
    """
    Test the creation of a beer without brewery exception.
    :param tmp_path: Test path of image.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    file_path = tmp_path / "test.png"
    file_path.write_bytes(b"fake image content")

    fake_data = {
        "name": "Test Beer",
        "beer_code": "TB001",
        "brewery": "test_brewery",
        "alcohol": 5.0,
        "volume": 0.2,
    }

    with patch("routes.beer.beer_routes.get_data_from_open_ai", return_value=fake_data):
        response = client_fixture.post(
            "/beer/upload",
            headers={"Authorization": f"Bearer {get_admin_token}"},
            files={"image": ("test.png", file_path.read_bytes(), "image/png")},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "BREWERY with name 'test_brewery' not found!"


def test_create_beer_without_admin_by_image(tmp_path, client_fixture, get_user_token):
    """
    Test the creation of a beer without admin exception.
    :param tmp_path: Test path of image.
    :param client_fixture: Test client.
    :param get_user_token: Test user token.
    :return: None
    """
    file_path = tmp_path / "test.png"
    file_path.write_bytes(b"fake image content")

    response = client_fixture.post(
        "/beer/upload",
        headers={"Authorization": f"Bearer {get_user_token}"},
        files={"image": ("test.png", file_path.read_bytes(), "image/png")},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid role"


def test_create_existing_beer_by_image(tmp_path, client_fixture, get_admin_token):
    """
    Test the creation of a beer by image exception.
    :param tmp_path: Test path of image.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    create_brewery(client_fixture)
    create_beer(client_fixture)
    file_path = tmp_path / "test.png"
    file_path.write_bytes(b"fake image content")

    fake_data = {
        "name": "test_beer",
        "beer_code": "1234",
        "brewery": "test_brewery",
        "alcohol": 0.1,
        "volume": 0.2,
    }

    with patch("routes.beer.beer_routes.get_data_from_open_ai", return_value=fake_data):
        response = client_fixture.post(
            "/beer/upload",
            headers={"Authorization": f"Bearer {get_admin_token}"},
            files={"image": ("test.png", file_path.read_bytes(), "image/png")},
        )

    assert response.status_code == 200
    assert (
        response.json()
        == "BEER `test_beer` with code `1234` from brewery 'test_brewery' already exists"
    )


def test_get_no_data_from_ai(tmp_path, client_fixture, get_admin_token):
    """
    Test the creation of a beer without data from AI exception.
    :param tmp_path: Test path of image.
    :param client_fixture: Test client.
    :param get_admin_token: Test admin token.
    :return: None
    """
    create_brewery(client_fixture)
    create_beer(client_fixture)
    file_path = tmp_path / "test.png"
    file_path.write_bytes(b"fake image content")

    fake_data = {"details": "some details"}

    with patch("routes.beer.beer_routes.get_data_from_open_ai", return_value=fake_data):
        response = client_fixture.post(
            "/beer/upload",
            headers={"Authorization": f"Bearer {get_admin_token}"},
            files={"image": ("test.png", file_path.read_bytes(), "image/png")},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "some details"
