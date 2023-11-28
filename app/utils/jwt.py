"""Utility functions for handling JWT tokens"""
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from app.errors import TokenDecodingException, TokenExpiredException
from app.utils.settings import settings


def create_jwt_token(uuid: str, secret: str, expires_delta: timedelta):
    """Function for creating a new JWT token, based on a UUID, secret and expiration time"""
    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": uuid,
        "exp": expire,
    }

    encoded_jwt = jwt.encode(payload, secret, algorithm="HS256")
    return encoded_jwt


def create_user_tokens(uuid: str):
    """Function for creating and returning the access and refresh tokens based on an user data"""
    access_token_expires = timedelta(minutes=settings.access_token_expiration)
    access_token = create_jwt_token(
        uuid, settings.access_token_private_key, access_token_expires
    )

    refresh_token_expires = timedelta(minutes=settings.refresh_token_expiration)
    refresh_token = create_jwt_token(
        uuid, settings.refresh_token_private_key, refresh_token_expires
    )

    return {"access_token": access_token, "refresh_token": refresh_token}


def decode_token_payload(token: str, secret: str):
    """Function for decoding a JWT token, based on a secret key, and return its payload"""
    try:
        payload = jwt.decode(token, secret, algorithms="HS256")
        return payload
    except ExpiredSignatureError as err:
        raise TokenExpiredException from err
    except JWTError as err:
        raise TokenDecodingException from err
