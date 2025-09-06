"""
Created by Fabian Gnatzig
Description: Main app of the beer backend.
"""

from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from auth.login_routes import router as login_router
from models.team_models import Team
from models.user_models import User
from routes import (
    beer_router,
    bring_beer_router,
    user_beer_router,
    user_router,
    brewery_router,
    event_router,
    season_router,
    team_router,
    service_router,
)

from dependencies import get_session, create_db, engine, pwd_context

SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(_app: FastAPI):  # pragma: no cover
    """
    Contextmanager for the FastAPI app.
    Initialize the DB.
    """
    create_db()

    with Session(engine) as session:
        stmt = select(User).where(User.role == "admin")
        admin = session.exec(stmt).first()

        if not admin:
            team = session.get(Team, 1)
            if not team:
                team = Team(name="team")
                session.add(team)
                session.commit()

            admin_user = User(
                username="admin",
                role="admin",
                password=pwd_context.hash("admin"),
                first_name="first_name",
                last_name="last_name",
                birthday="2000-01-01",
                team_id=1,
            )
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)

    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bier.gnatzig.eu", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(beer_router)
app.include_router(brewery_router)
app.include_router(team_router)
app.include_router(user_router)
app.include_router(season_router)
app.include_router(event_router)
app.include_router(bring_beer_router)
app.include_router(user_beer_router)
app.include_router(service_router)
app.include_router(login_router)
