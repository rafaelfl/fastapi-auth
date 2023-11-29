"""Utility functions for handling authentication"""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from redis import Redis
from app.errors import TokenDecodingException, TokenExpiredException
from app.services.blocklist import BlockListService
from app.utils.settings import settings
from app.utils.jwt import decode_token_payload
from app.utils.redis import get_redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_access_token(token: Annotated[str, Depends(oauth2_scheme)] = None):
    """Function for extracting Authorization header and return it"""
    return token


def get_access_token_user_uuid(
    token: Annotated[str, Depends(oauth2_scheme)],
    redis: Annotated[Redis, Depends(get_redis)] = None,
):
    """Function for extracting Authorization header and return the associated user UUID key"""

    if redis:
        blocklist_service = BlockListService(redis)
        is_blocked = blocklist_service.is_token_blocked(token)

        if is_blocked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Reusing a signed-out token is not allowed",
            )

    return decode_user_uuid(token, settings.access_token_private_key)


def decode_user_uuid(token: str, secret: str):
    """Function for decoding a JWT token, using an specific secret, and return its UUID key"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = decode_token_payload(token, secret)
        user_uuid = str(payload["sub"])

        return user_uuid
    except KeyError as err:
        raise credentials_exception from err
    except TokenDecodingException as err:
        raise credentials_exception from err
    except TokenExpiredException as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token expired",
        ) from err
