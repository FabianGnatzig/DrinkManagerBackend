"""
Created by Fabian Gnatzig

Description: Models of events.
"""
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .beer_models import BringBeer
    from .season_models import Season


class EventBase(SQLModel):
    """
    Base data class of event.
    """
    name: str
    season_id: int = Field(default=None, foreign_key="season.id")
    event_date: date

class Event(EventBase, table=True):
    """
    Table class of event.
    """
    id: int | None = Field(default=None, primary_key=True)
    season: Optional["Season"] = Relationship(back_populates="events")
    bring_beer: list["BringBeer"] = Relationship(back_populates="event")

class EventUpdate(EventBase):
    """
    Update class of event.
    """
    name: str | None = None
    season_id: int | None = None
    event_date: date | None = None
