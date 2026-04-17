"""
Created by Fabian Gnatzig
Description: Models of teams.
"""

import uuid
from typing import List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user_models import User
    from .season_models import Season


class TeamBase(SQLModel):
    """
    Base data class of team.
    """

    name: str = Field(index=True)


class Team(TeamBase, table=True):
    """
    Table class of team.
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    users: List["User"] | None = Relationship(back_populates="team")
    seasons: List["Season"] | None = Relationship(back_populates="team")


class TeamUpdate(TeamBase):
    """
    Update class of team.
    """

    name: str | None = None
