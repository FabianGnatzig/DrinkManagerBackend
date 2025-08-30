"""
Created by Fabian Gnatzig
Description: Http routes of events.
"""

from datetime import datetime
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from dependencies import get_session
from models.event_models import Event

router = APIRouter(prefix="/event", tags=["Event"])


@router.get("/all")
def read_all_events(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Event]:
    """
    Reads all event instances.
    :param session: The db session.
    :param offset: Start offset.
    :param limit: Query limit.
    :return: List of all events.
    """
    statement = select(Event).offset(offset).limit(limit)
    events = session.exec(statement).all()
    return events


@router.get("/{event_id}")
def get_event_id(event_id: int, session: Session = Depends(get_session)) -> dict:
    """
    Searches for an event with id.
    :param event_id: ID of an event.
    :param session: The db session.
    :return: Dictionary with event and related instances.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=404, detail=f"Event with id '{event_id}' not found!"
        )

    event_json = event.model_dump()
    if event.season:
        event_json.update({"season": event.season.model_dump()})
    if event.bring_beer:
        event_json.update({"bring_beer": event.bring_beer})
    return event_json


@router.get("/name/{event_name}")
def get_event_name(event_name: str, session: Session = Depends(get_session)) -> dict:
    """
    Searches for an event with name.
    :param event_name: Name of an event to search for.
    :param session: The db session.
    :return: Dictionary with event and related instances.
    """
    statement = select(Event).where(Event.name == event_name)
    try:
        event = session.exec(statement).one()
    except Exception as ex:
        raise HTTPException(
            status_code=404, detail=f"Event with name '{event_name}' not found!"
        ) from ex

    event_json = event.model_dump()
    if event.season:
        event_json.update({"season": event.season.model_dump()})
    if event.bring_beer:
        event_json.update({"bring_beer": event.bring_beer})
    return event_json


@router.post("/add")
def create_event(event_data: dict, session: Session = Depends(get_session)) -> Event:
    """
    Creates an event instance.
    :param event_data: The event data.
    :param session: The db session.
    :return: The created event instance.
    """
    if event_data["name"] == "":
        raise HTTPException(status_code=400, detail="Invalid event")

    try:
        event_data["event_date"] = datetime.strptime(
            event_data["event_date"], "%Y-%m-%d"
        ).date()
    except Exception as ex:
        raise HTTPException(status_code=400, detail="Invalid date") from ex

    event = Event(**event_data)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.delete("/{event_id}")
def delete_event(event_id: int, session: Session = Depends(get_session)) -> dict:
    """
    Deletes an event with id.
    :param event_id: ID of an event.
    :param session: The db session.
    :return: {"ok": True} if succeeded.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=404, detail=f"Event with id '{event_id}' not found!"
        )

    session.delete(event)
    session.commit()
    return {"ok": True}


@router.patch("/{event_id}")
def update_event(
    event_id: int, event: Event, session: Session = Depends(get_session)
) -> Event:
    """
    Updates the data of an event.
    :param event_id: ID of the event to be edited.
    :param event: Edited event data.
    :param session: The db session.
    :return: Edited event instance.
    """
    event_db = session.get(Event, event_id)
    if not event_db:
        raise HTTPException(
            status_code=404, detail=f"Event with id '{event_id}' not found!"
        )

    event_data = event.model_dump(exclude_unset=True)
    event_db.sqlmodel_update(event_data)
    session.add(event_db)
    session.commit()
    session.refresh(event_db)
    return event_db
