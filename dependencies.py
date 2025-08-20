"""
Created by Fabian Gnatzig

Description: Shared methods for project.
"""
from sqlmodel import Session, create_engine, SQLModel

SQLITE_FILE_NAME = "database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

connect_args = {"check_same_thread": False}
engine = create_engine(SQLITE_URL, connect_args=connect_args)

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
