from __future__ import annotations

from pydantic import BaseModel


class UserToken(BaseModel):
    userToken: str
