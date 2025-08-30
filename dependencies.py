"""
Created by Fabian Gnatzig
Description: Shared methods for project.
"""

import os

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, create_engine, SQLModel

load_dotenv()

DB = os.getenv("DATABASE")

engine = create_engine(DB)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("HASH_KEY")


def create_db():
    """
    Creates the db.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Returns the session instance.
    :return: The session instance.
    """
    with Session(engine) as session:
        yield session
