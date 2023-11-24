"""Pydantic user authentication schema classes"""
from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    """Base user schema class"""
    username: str

class UserSignIn(UserBase):
    """User signin schema class for performing login"""
    password: str

class UserCreate(UserSignIn):
    """User create schema class for user creation"""
    name: str

class User(UserBase):
    """User schema class for storing data coming from the database"""
    uuid: str
    name: str
    last_update: datetime
