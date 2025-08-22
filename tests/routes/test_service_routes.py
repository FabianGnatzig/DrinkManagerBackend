"""
Created by Fabian Gnatzig
Description: Unittest for service routes
"""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from tests.helper_methods import create_beer, create_user, create_user_beer, create_bring_beer


def test_read_open_beers(client_fixture):
    """
    Tests to read all open beer (unlinked user_beer).
    :param client_fixture: Test client.
    :return: None
    """
    create_user(client_fixture)
    create_user_beer(client_fixture)

    response = client_fixture.get("/service/all_open_beer")
    assert response.status_code == 200
    assert response.json()[0]["kind"] == "test_kind"
    assert response.json()[0]["user"] == "first last"


def test_read_beer_amounts(client_fixture):
    """
    Test read the amount of linked user- and bring-beer of a user.
    :param client_fixture: Test client.
    :return: None
    """
    create_beer(client_fixture)
    create_user(client_fixture)


    response = client_fixture.get("/service/beer_amount")
    assert response.status_code == 200
    assert response.json()[0]["user"] == "first last"
    assert response.json()[0]["amount"] == 0

    create_user_beer(client_fixture)
    create_bring_beer(client_fixture)

    response = client_fixture.get("/service/beer_amount")
    assert response.status_code == 200
    assert response.json()[0]["user"] == "first last"
    assert response.json()[0]["amount"] == 1


def test_check_birthday(client_fixture):
    """
    Test the check birthday route.
    :param client_fixture: Test client.
    :return: None
    """
    date = datetime.today().date()
    test_payload = {
        "username": "a",
        "first_name": "fa",
        "last_name": "la",
        "birthday": f"{date + timedelta(days=1)}",
        "team_id": 1,
        "password": "pswd",
        "role": "test_role",
    }
    response =  client_fixture.post("/user/add", json=test_payload)
    assert response.status_code == 200

    test_payload["username"] = "b"
    test_payload["first_name"] = "fb"
    test_payload["last_name"] = "lb"
    test_payload["birthday"] = f"{date + relativedelta(months=1)}"
    response = client_fixture.post("/user/add", json=test_payload)
    assert response.status_code == 200

    test_payload["username"] = "c"
    test_payload["first_name"] = "fc"
    test_payload["last_name"] = "lc"
    test_payload["birthday"] = f"{date}"
    response = client_fixture.post("/user/add", json=test_payload)
    assert response.status_code == 200

    response = client_fixture.get("/user/all")
    assert len(response.json()) == 3

    response = client_fixture.get("/service/check_birthday")
    assert response.status_code == 200

    response = client_fixture.get("/service/all_open_beer")
    assert response.status_code == 200
    assert response.json()[0]["user"] == "fc lc"
    assert response.json()[0]["user_id"] == 3
