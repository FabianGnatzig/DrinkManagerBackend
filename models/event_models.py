"""
Created by Fabian Gnatzig
Description: Models of events.
"""

import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

from models.types import UUIDType

if TYPE_CHECKING:
    from .beer_models import BringBeer
    from .season_models import Season


class EventBase(SQLModel):
    """
    Base data class of event.
    """

    name: str
    season_id: UUIDType = Field(default=None, foreign_key="season.id")
    event_date: date


class Event(EventBase, table=True):
    """
    Table class of event.
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    season: Optional["Season"] = Relationship(back_populates="events")
    bring_beer: list["BringBeer"] = Relationship(back_populates="event")


class EventUpdate(EventBase):
    """
    Update class of event.
    """

    name: str | None = None
    season_id: UUIDType = None
    event_date: date | None = None
