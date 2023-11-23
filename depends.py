"""General dependencies functions"""
from db.connection import SessionLocal


def get_db():
    """Function for retrieving a global Session database connection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
