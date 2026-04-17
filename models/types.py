"""
Created by Fabian Gnatzig
Description: Shared model types and validators.
"""

import uuid
from typing import Annotated

from pydantic import BeforeValidator


def _parse_uuid(v) -> uuid.UUID | None:
    if v is None or isinstance(v, uuid.UUID):
        return v
    return uuid.UUID(v)


UUIDType = Annotated[uuid.UUID | None, BeforeValidator(_parse_uuid)]
