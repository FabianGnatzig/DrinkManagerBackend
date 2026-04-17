"""
Created by Fabian Gnatzig
Description: Models of season.
"""

import uuid
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from models.types import UUIDType

if TYPE_CHECKING:
    from .team_models import Team
    from .event_models import Event


class SeasonBase(SQLModel):
    """
    Base data class of Season.
    """

    name: str
    team_id: UUIDType = Field(default=None, foreign_key="team.id")


class Season(SeasonBase, table=True):
    """
    Table class of season.
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    team: Optional["Team"] = Relationship(back_populates="seasons")
    events: list["Event"] = Relationship(back_populates="season")


class SeasonUpdate(SeasonBase):
    """
    Update class of season.
    """

    name: str | None = None
    team_id: UUIDType = None
