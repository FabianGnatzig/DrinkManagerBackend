"""
Created by Fabian Gnatzig
Description: Http routes of events.
"""

from datetime import datetime
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from auth.auth_methods import is_admin
from dependencies import get_session, oauth2_scheme
from exceptions import NotFoundException, IncompleteException, InvalidException
from models.event_models import Event

router = APIRouter(prefix="/event", tags=["Event"])
TYPE = "EVENT"


@router.get("/all")
def read_all_events(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Event]:
    """
    Reads all event instances.
    :param session: DB session.
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
    :param session: DB session.
    :return: Dictionary with event and related instances.
    """
    event = session.get(Event, event_id)
    if not event:
        raise NotFoundException(TYPE, data_id=event_id)

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
    :param session: DB session.
    :return: Dictionary with event and related instances.
    """
    statement = select(Event).where(Event.name == event_name)
    try:
        event = session.exec(statement).one()
    except Exception as ex:
        raise NotFoundException(TYPE, data_name=event_name) from ex

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
    :param event_data: Event data.
    :param session: DB session.
    :return: Created event instance.
    """
    if event_data["name"] == "":
        raise IncompleteException(TYPE)

    try:
        event_data["event_date"] = datetime.strptime(
            event_data["event_date"], "%Y-%m-%d"
        ).date()
    except Exception as ex:
        raise InvalidException("event_date") from ex

    event = Event(**event_data)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> dict:
    """
    Deletes an event with id.
    :param event_id: ID of an event.
    :param token: User jwt-token.
    :param session: DB session.
    :return: {"ok": True} if succeeded.
    """
    is_admin(token)

    event = session.get(Event, event_id)
    if not event:
        raise NotFoundException(TYPE, data_id=event_id)

    session.delete(event)
    session.commit()
    return {"ok": True}


@router.patch("/{event_id}")
def update_event(
    event_id: int, event: Event, session: Session = Depends(get_session)
) -> type[Event]:
    """
    Updates the data of an event.
    :param event_id: ID of the event to be edited.
    :param event: Edited event data.
    :param session: DB session.
    :return: Edited event instance.
    """
    event_db = session.get(Event, event_id)
    if not event_db:
        raise NotFoundException(TYPE, data_id=event_id)

    event_data = event.model_dump(exclude_unset=True)
    event_db.sqlmodel_update(event_data)
    session.commit()
    session.refresh(event_db)
    return event_db
