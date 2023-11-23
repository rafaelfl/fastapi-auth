"""Create database connection session object"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.settings import settings

engine = create_engine(
    settings.db_url,
    echo=True,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker()
SessionLocal.configure(autocommit=False, autoflush=False, bind=engine)

session = SessionLocal()
