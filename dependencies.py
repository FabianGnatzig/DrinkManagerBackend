"""
Created by Fabian Gnatzig

Description: Shared methods for project.
"""
import os

from dotenv import load_dotenv
from sqlmodel import Session, create_engine, SQLModel

load_dotenv()

DB = os.getenv("DATABASE")

# connect_args = {"check_same_thread": False}

engine = create_engine(DB)

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
