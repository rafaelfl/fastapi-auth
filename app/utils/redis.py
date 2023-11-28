"""Module containing Redis utility function, such as the dependency injection function"""
from redis import from_url
from app.utils.settings import settings

def get_redis():
    """Function for retrieving a Redis database connection"""
    r = from_url(url=settings.redis_url, encoding="utf-8", decode_responses=True)
    r.ping()
    try:
        yield r
    finally:
        r.close()
