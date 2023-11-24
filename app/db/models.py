"""SQLAlchemy ORM models"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from .base import Base


def generate_uuid():
    """Function for UUID primary key generation"""
    return str(uuid.uuid4())


class UserModel(Base):
    """Database user ORM model"""
    __tablename__ = "user"

    uuid = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True)
    password = Column(String)
    name = Column(String)
    last_update = Column(DateTime, default=datetime.utcnow)
