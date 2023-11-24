"""Application general settings"""
from pydantic_settings import BaseSettings
from decouple import config

ACCESS_TOKEN_PRIVATE_KEY = config("ACCESS_TOKEN_PRIVATE_KEY")
REFRESH_TOKEN_PRIVATE_KEY = config("REFRESH_TOKEN_PRIVATE_KEY")

ACCESS_TOKEN_EXPIRATION = config("ACCESS_TOKEN_EXPIRATION", cast=int)
REFRESH_TOKEN_EXPIRATION = config("REFRESH_TOKEN_EXPIRATION", cast=int)

DB_URL = config("DB_URL")

class Settings(BaseSettings):
    """Class that groups all loaded application settings"""
    db_url: str = DB_URL
    access_token_private_key: str = ACCESS_TOKEN_PRIVATE_KEY
    refresh_token_private_key: str = REFRESH_TOKEN_PRIVATE_KEY
    access_token_expiration: int = ACCESS_TOKEN_EXPIRATION
    refresh_token_expiration: int = REFRESH_TOKEN_EXPIRATION


settings = Settings()
