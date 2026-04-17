"""
Created by Fabian Gnatzig
Description: Models of beers.
"""

import uuid
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from models.types import UUIDType

if TYPE_CHECKING:
    from .brewery_models import Brewery
    from .user_models import User
    from .event_models import Event


class BeerBase(SQLModel):
    """
    Base data class of beer.
    """

    name: str = Field(index=True)
    beer_code: str = Field(index=True)
    brewery_id: UUIDType = Field(default=None, foreign_key="brewery.id")
    alcohol: float = 0.0
    volume: float = 0.0


class Beer(BeerBase, table=True):
    """
    Table class of beer.
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    brewery: Optional["Brewery"] = Relationship(back_populates="beers")
    bring_beer: list["BringBeer"] = Relationship(back_populates="beer")


class BeerUpdate(BeerBase):
    """
    Update class of beer.
    """

    name: str | None = None
    beer_code: str | None = None
    brewery_id: UUIDType = None
    alcohol: float | None = None
    volume: float | None = None


class UserBeerBase(SQLModel):  #
    """
    Base data class if user beer.
    """

    user_id: UUIDType = Field(default=None, foreign_key="user.id")
    kind: str


class UserBeer(UserBeerBase, table=True):
    """
    Table class of user beer.
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user: Optional["User"] = Relationship(back_populates="user_beer")
    bring_beer: Optional["BringBeer"] = Relationship(back_populates="user_beer")


class UserBeerUpdate(UserBeerBase):
    """
    Update class of user beer.
    """

    user_id: UUIDType = None
    kind: str | None = None


class BringBeerBase(SQLModel):
    """
    Base data class of bring beer.
    """

    event_id: UUIDType = Field(default=None, foreign_key="event.id")
    user_id: UUIDType = Field(default=None, foreign_key="user.id")
    user_beer_id: UUIDType = Field(default=None, foreign_key="userbeer.id")
    beer_id: UUIDType = Field(default=None, foreign_key="beer.id")
    done: bool = False


class BringBeer(BringBeerBase, table=True):
    """
    Table class of bring beer.
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_beer: Optional["UserBeer"] = Relationship(back_populates="bring_beer")
    user: Optional["User"] = Relationship(back_populates="bring_beer")
    event: Optional["Event"] = Relationship(back_populates="bring_beer")
    beer: Optional["Beer"] = Relationship(back_populates="bring_beer")


class BringBeerUpdate(BringBeerBase):
    """
    Update class of bring beer.
    """

    event_id: UUIDType = None
    user_id: UUIDType = None
    user_beer_id: UUIDType = None
    beer_id: UUIDType = None
    done: bool | None = None
