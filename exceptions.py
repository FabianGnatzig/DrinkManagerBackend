"""
Created by Fabian Gnatzig
Description: Configured Exceptions
"""

from typing import Optional

from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """
    Not found exception when searching for name, code or ID.
    """

    def __init__(
        self,
        type_name: str,
        data_name: Optional[str] = None,
        data_id: Optional[int] = None,
        data_code: Optional[str] = None,
    ):
        if data_name:
            super().__init__(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{type_name} with name '{data_name}' not found!",
            )
        if data_id:
            super().__init__(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{type_name} with id '{data_id}' not found!",
            )
        if data_code:
            super().__init__(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{type_name} with code '{data_code}' not found!",
            )


class IncompleteException(HTTPException):
    """
    Incomplete exception.
    """

    def __init__(self, type_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incomplete {type_name}",
        )


class InvalidException(HTTPException):
    """
    Invalid exception.
    """

    def __init__(self, type_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {type_name}",
        )


class InvalidTokenException(HTTPException):
    """
    Invalid token exception.
    """
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


class InvalidRoleException(HTTPException):
    """
    Invalid role exception.
    """
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid role",
        )


class InvalidUserException(HTTPException):
    """
    Invalid user exception.
    """
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user",
        )
