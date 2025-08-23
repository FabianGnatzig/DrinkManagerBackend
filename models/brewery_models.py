"""
Created by Fabian Gnatzig

Description: Models of brewerys.
"""

from typing import List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .beer_models import Beer


class BreweryBase(SQLModel):
    """
    Base data class of brewery.
    """

    name: str = Field(index=True)
    city: str = Field(index=True)
    country: str = Field(index=True)


class Brewery(BreweryBase, table=True):
    """
    Table class of brewery.
    """

    id: int | None = Field(default=None, primary_key=True)
    beers: List["Beer"] | None = Relationship(back_populates="brewery")


class BreweryUpdate(BreweryBase):
    """
    Update class of brewery.
    """

    name: str | None = None
    city: str | None = None
    country: str | None = None
