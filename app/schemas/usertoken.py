"""Pydantic usertoken authentication schema classes"""
from datetime import datetime
from pydantic import BaseModel


class UserTokenCreate(BaseModel):
    """UserToken create schema class used for creating a new schema record"""

    uuid: str
    refresh_token: str


class UserToken(UserTokenCreate):
    """UserToken schema class for retrieving the user uuid and its token"""

    created_at: datetime
