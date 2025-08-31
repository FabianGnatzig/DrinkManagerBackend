"""
Created by Fabian Gnatzig
Description: Token classes.
"""

from sqlmodel import SQLModel


class Token(SQLModel):
    """
    Class, how the token will returned.
    """

    access_token: str
    token_type: str
