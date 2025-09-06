"""
Created by Fabian Gnatzig
Description: HTTP routes of service.
"""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from dependencies import get_session
from models.beer_models import BringBeer, UserBeer, Beer
from models.brewery_models import Brewery
from models.user_models import User
from routes.beer.beer_routes import read_beer_name, create_beer
from routes.beer.user_beer_routes import create_user_beer
from routes.brewery.brewery_routes import read_brewery_name, create_brewery

router = APIRouter(prefix="/service", tags=["Service"])


@router.get("/all_open_beer")
def read_open_beer(session: Session = Depends(get_session)) -> list[UserBeer]:
    """
    Reads all unlinked user_beer. Unlinked user_beer are open beer.
    :param session: DB session.
    :return: All open user beers.
    """
    # pylint: disable=singleton-comparison
    statement = (
        select(UserBeer)
        .outerjoin(BringBeer, UserBeer.id == BringBeer.user_beer_id)
        .where(BringBeer.id == None)
    )
    results = session.exec(statement).all()

    open_user_beers = []

    for result in results:
        user = session.get(User, result.user_id)

        open_user_beers.append(
            {
                "user": f"{user.first_name} {user.last_name}",
                "user_id": user.id,
                "user_beer_id": result.id,
                "kind": result.kind,
            }
        )

    return open_user_beers


@router.get("/beer_amount")
def read_number_beer(session: Session = Depends(get_session)) -> list[dict]:
    """
    Reads the beer amount of all users.
    :param session: DB Session.
    :return: List of all users with amount of brought beer.
    """
    statement = select(User)
    results = session.exec(statement).all()

    beer_amount = []
    for user in results:
        user_dict = {}
        user_dict.update({"user": f"{user.first_name} {user.last_name}"})

        if user.bring_beer:
            user_dict.update({"amount": len(user.bring_beer)})
        else:
            user_dict.update({"amount": 0})

        if user.user_beer:
            user_dict.update({"included_fine": len(user.user_beer)})
        else:
            user_dict.update({"included_fine": 0})

        beer_amount.append(user_dict)

    sorted_amounts = sorted(
        beer_amount, key=lambda item: item["amount"] - item["included_fine"]
    )
    return sorted_amounts


@router.get("/check_birthday")
def check_birthday(session: Session = Depends(get_session)) -> bool:
    """
    Checks if a user has birthday and create an uer_beer.
    :param session: DB session.
    :return: True
    """
    users = session.exec(select(User)).all()

    for user in users:
        if (
            user.birthday.day == datetime.today().day
            and user.birthday.month == datetime.today().month
        ):
            user_beer = UserBeer(user_id=user.id, kind="birthday")
            create_user_beer(user_beer, session=session)

    return True


@router.get("/setup")
def setup_brewery_and_beer(session: Session = Depends(get_session)):
    """
    Creates brewery and beer from data.
    :param session: DB session.
    :return: None
    """
    setup_brewery(session)
    setup_beer(session)


def setup_beer(session: Session):
    """
    Setup beer from beer.json.
    :param session: DB session.
    :return: None
    """
    with open("data/beers.json", encoding="utf-8") as beer_file:
        beers = json.load(beer_file)

        for beer_data in beers["beers"]:
            try:
                read_beer_name(beer_data["name"], session)
            except HTTPException:
                create_beer(Beer(**beer_data), session)


def setup_brewery(session: Session):
    """
    Setup brewery from brewery.json.
    :param session: DB session.
    :return: None
    """
    with open("data/brewerys.json", encoding="utf-8") as brewery_file:
        brewery = json.load(brewery_file)

        for brewery_data in brewery["brewerys"]:
            try:
                read_brewery_name(brewery_data["name"], session)
            except HTTPException:
                create_brewery(Brewery(**brewery_data), session)
