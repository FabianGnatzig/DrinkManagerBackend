"""
Created by Fabian Gnatzig

Description: Main app of the beer backend.
"""
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session


from routers import (beer_router, bring_beer_router, user_beer_router, user_router, brewery_router,
                     event_router, season_router, team_router, service_router)

from dependencies import get_session, create_db

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bier.gnatzig.eu", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
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

@app.on_event("startup")
def on_startup():
    """
    Creates db on startup
    """
    create_db()

@app.get("/")
async def root():
    """
    Root route of app.
    :return: Test data.
    """
    return {"message": "HelloWorld"}
