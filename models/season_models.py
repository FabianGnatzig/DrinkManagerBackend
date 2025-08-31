"""
Created by Fabian Gnatzig
Description: Models of season.
"""

from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .team_models import Team
    from .event_models import Event


class SeasonBase(SQLModel):
    """
    Base data class of Season.
    """

    name: str
    team_id: int = Field(default=None, foreign_key="team.id")


class Season(SeasonBase, table=True):
    """
    Table class of season.
    """

    id: int | None = Field(default=None, primary_key=True)
    team: Optional["Team"] = Relationship(back_populates="seasons")
    events: list["Event"] = Relationship(back_populates="season")


class SeasonUpdate(SeasonBase):
    """
    Update class of season.
    """

    name: str | None = None
    team_id: int | None = None
