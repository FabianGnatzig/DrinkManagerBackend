"""
Created by Fabian Gnatzig
Description: Models of users.
"""

from datetime import date
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from models.beer_models import BringBeer

if TYPE_CHECKING:
    from .team_models import Team
    from .beer_models import UserBeer


class UserBase(SQLModel):
    """
    Base data class of user.
    """

    username: str
    first_name: str
    last_name: str
    birthday: date
    team_id: int = Field(default=None, foreign_key="team.id")
    password: str
    role: str


class User(UserBase, table=True):
    """
    Table class of user.
    """

    id: int | None = Field(default=None, primary_key=True)
    team: Optional["Team"] = Relationship(back_populates="users")
    user_beer: list["UserBeer"] = Relationship(back_populates="user")
    bring_beer: list["BringBeer"] = Relationship(back_populates="user")


class UserUpdate(UserBase):
    """
    Update class of user.
    """

    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birthday: date | None = None
    team_id: int | None = None
    password: str | None = None
    role: str | None = None


def get_public_user(user: User) -> dict:
    """
    Converts the user to dict and removes the team_id and the password.
    :param user: The user object to be converted.
    :return: The converted user dictionary.
    """
    user_json = user.model_dump()
    user_json.pop("password", None)
    user_json.pop("team_id", None)
    return user_json
