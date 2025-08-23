"""
Created by Fabian Gnatzig
Description: Unittests of user routes.
"""

from datetime import date

import pytest

from models.user_models import UserBase, get_public_user


def test_get_public_user():
    """
    Tests the public user class.
    :return: None
    """
    user = UserBase(
        username="testuser",
        first_name="Test",
        last_name="User",
        birthday=date(1990, 1, 1),
        team_id=1,
        password="secret",
        role="admin",
    )

    assert user.username == "testuser"

    global_user = get_public_user(user)
    with pytest.raises(KeyError):
        assert not global_user["password"]

    with pytest.raises(KeyError):
        assert not global_user["team_id"]

    assert global_user["username"] == "testuser"
