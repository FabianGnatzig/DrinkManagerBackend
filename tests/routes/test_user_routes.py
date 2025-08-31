"""
Created by Fabian Gnatzig
Description: Unittests for user routes.
"""

from tests.helper_methods import (
    create_user,
    create_bring_beer,
    create_beer,
    create_team,
    create_user_beer,
)


def test_read_user(client_fixture):
    """
    Test read user.
    :param client_fixture: Test client.
    :return: None
    """
    create_user(client_fixture)

    response = client_fixture.get("/user/all")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_read_user_id_as_admin(client_fixture, get_admin_token):
    """
    Test read user by id with admin authentication.
    :param client_fixture: Test client.
    :return: None
    """
    create_user(client_fixture)
    create_bring_beer(client_fixture)
    create_beer(client_fixture)
    create_user_beer(client_fixture)
    create_team(client_fixture)

    response = client_fixture.get(
        "/user/1", headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "name"
    assert response.json()["team"]
    assert response.json()["bring_beer"]
    assert response.json()["user_beer"]


def test_read_user_id_as_user(client_fixture, get_user_token):
    """
    Test read user by id with admin authentication.
    :param client_fixture: Test client.
    :return: None
    """
    create_user(client_fixture)
    create_bring_beer(client_fixture)
    create_beer(client_fixture)
    create_user_beer(client_fixture)
    create_team(client_fixture)

    response = client_fixture.get(
        "/user/1", headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "name"
    assert response.json()["team"]
    assert response.json()["bring_beer"]
    assert response.json()["user_beer"]


def test_read_wrong_user_id(client_fixture, get_admin_token):
    """
    Test read not existing user by id as admin.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = "324234"

    create_user(client_fixture)

    response = client_fixture.get(
        f"/user/{wrong_id}", headers={"Authorization": f"Bearer {get_admin_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == f"User with id '{wrong_id}' not found!"


def test_auth_read_wrong_user_id(client_fixture, get_user_token):
    """
    Test read user by id as wrong user.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = "2"

    create_user(client_fixture)
    create_user(client_fixture)

    response = client_fixture.get(
        f"/user/{wrong_id}", headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "You try to access an other user"


def test_read_user_name(client_fixture):
    """
    Tests read a user by name.
    :param client_fixture: Test client.
    :return: None
    """
    user_name = "name"
    create_team(client_fixture)
    create_user(client_fixture)
    create_bring_beer(client_fixture)
    create_beer(client_fixture)
    create_user_beer(client_fixture)

    response = client_fixture.get(f"/user/name/{user_name}")
    assert response.status_code == 200
    assert response.json()["team_id"] == 1
    assert response.json()["team"]
    assert response.json()["bring_beer"]
    assert response.json()["user_beer"]


def test_read_wrong_user_name(client_fixture):
    """
    Test read wrong user by name.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_name = "wrong"

    create_user(client_fixture)

    response = client_fixture.get(f"/user/name/{wrong_name}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"User with last name '{wrong_name}' not found!"


def test_add_user_with_wrong_birthday(client_fixture):
    """
    Test add a user with wrong birthday.
    :param client_fixture: Test client.
    :return: None
    """
    test_payload = {
        "username": "name",
        "first_name": "first",
        "last_name": "last",
        "birthday": "22-2-2025",
        "team_id": 1,
        "password": "pswd",
        "role": "test_role",
    }

    response = client_fixture.post("/user/add", json=test_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid date"


def test_delete_user(client_fixture):
    """
    Test the deleting of a user.
    :param client_fixture: Test client.
    :return: None
    """
    create_user(client_fixture)

    response = client_fixture.delete("/user/1")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_delete_wrong_user(client_fixture):  #
    """
    Test the deletion of a user exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = 321321

    response = client_fixture.delete(f"/user/{wrong_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"User with id '{wrong_id}' not found!"


def test_update_user_name(client_fixture):
    """
    Test the update of a user.
    :param client_fixture: Test client.
    :return: None
    """
    create_user(client_fixture)

    new_name = "new_test_user"
    test_payload = {"first_name": f"{new_name}"}

    response = client_fixture.patch("/user/1", json=test_payload)
    assert response.status_code == 200
    assert response.json()["first_name"] == new_name
    assert response.json()["team_id"] == 1


def test_update_wrong_user(client_fixture):
    """
    Test the update of a user exception.
    :param client_fixture: Test client.
    :return: None
    """
    wrong_id = 321321
    response = client_fixture.patch(f"/user/{wrong_id}", json={})
    assert response.status_code == 404
    assert response.json()["detail"] == f"User with id '{wrong_id}' not found!"
