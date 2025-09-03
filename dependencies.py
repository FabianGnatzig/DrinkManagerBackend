"""
Created by Fabian Gnatzig
Description: Shared methods for project.
"""

import json
import os

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from openai import OpenAI
from passlib.context import CryptContext
from sqlmodel import Session, create_engine, SQLModel

load_dotenv()

DB = os.getenv("DATABASE")

engine = create_engine(DB)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("HASH_KEY")

client = OpenAI(api_key=f"{os.getenv("OPEN_API_KEY")}")

OPEN_AI_REQUEST = (
    "Can you get me following data from this beer label as json:"
    "name: string, brewery or label (Like Gösser or Edelweiss):string as key brewery,"
    "alcohol:float, volume:float (normal is 0.5 or 0.33 please round),"
    "barcode number:string as key beer_code without whitespaces."
    "Check the data complies with the rules:"
    "When the label or name of the brewery is inside the name of the beer, "
    "please remove it from the beer name."
    "If the words 'beer' or 'bier' is inside the name, keep it inside!"
    "Use oe instead of ö. Use ae instead of ä. Use ue instead of ü. Use ss instead of ß."
)


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


def get_json_from_open_ai_response(response: str):
    """
    Creates a dictionary out of the response message from Open AI.
    :param response: Response message from Open AI.
    :return: Dictionary object.
    """
    try:
        data = response.split("```")[1].lstrip("json")
        return json.loads(data)
    except Exception:
        return {"details": "No data found!"}
