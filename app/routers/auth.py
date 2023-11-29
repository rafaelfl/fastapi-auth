"""Endpoints for authentication"""
from typing import Annotated, Union
from datetime import datetime, timedelta
from fastapi import APIRouter, Cookie, HTTPException, Response, Depends, status
from fastapi.responses import JSONResponse
from redis import Redis
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.connection import get_db
from app.schemas.response_result import ResponseResult
from app.schemas.user import UserCreate, UserSignIn
from app.schemas.usertoken import UserTokenCreate
from app.services.blocklist import BlockListService
from app.services.usertoken import UserTokenService
from app.utils.settings import settings
from app.utils.auth import (
    decode_user_uuid,
    get_access_token,
    get_access_token_user_uuid,
)
from app.utils.jwt import create_user_tokens
from app.utils.redis import get_redis
from app.services.user import UserService

router = APIRouter()


@router.post("/register", response_model=ResponseResult)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Endpoint for registering a new user"""
    user_service = UserService(db)

    result_user = user_service.create_user(user)
    return {"status": True, "message": "Success", "data": result_user}


@router.post("/login", response_model=ResponseResult)
def login_user(
    user_signin: UserSignIn,
    response: Response,
    refresh_token: Annotated[Union[str, None], Cookie()] = None,
    db: Session = Depends(get_db),
):
    """Endpoint for performing a username/password login"""
    user_service = UserService(db)
    usertoken_service = UserTokenService(db)

    try:
        # in case the sign-in is receiving an existing refresh_token cookie...
        if refresh_token:
            # looks for an existing and registered refresh token
            user_uuid = decode_user_uuid(
                refresh_token, settings.refresh_token_private_key
            )

            user_token = usertoken_service.find_usertoken(refresh_token)

            # if the refresh token doesn't exist in the database, it means that someone
            # else rotated it! So, let's clear all valid refresh tokens
            if user_token is None:
                usertoken_service.remove_all_user_tokens_by_uuid(user_uuid)
            else:
                usertoken_service.remove_user_token_by_token(user_token.refresh_token)

            response.delete_cookie(key="refresh_token")
    except HTTPException:
        pass  # ignore errors when decoding token and continue the login
    except SQLAlchemyError:
        pass  # ignore errors when querying or deleting usertoken entries and continue the login

    user_uuid = user_service.signin(user_signin)

    tokens = create_user_tokens(user_uuid)
    new_refresh_token = tokens["refresh_token"]

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        expires=settings.refresh_token_expiration * 60,
        httponly=True,
        samesite="lax",
        secure=True,
    )

    usertoken_service.insert_user_token(
        UserTokenCreate(uuid=user_uuid, refresh_token=new_refresh_token)
    )

    return {"status": True, "message": "Success", "data": tokens}


@router.post("/refresh", response_model=ResponseResult)
def refresh_tokens(
    response: Response,
    refresh_token: Annotated[Union[str, None], Cookie()] = None,
    db: Session = Depends(get_db),
):
    """Endpoint for refreshing an expired access token"""
    user_service = UserService(db)
    usertoken_service = UserTokenService(db)

    user_uuid = user_service.refresh_user_token(refresh_token)

    # let's delete the refresh token to rotate it
    response.delete_cookie(key="refresh_token")

    tokens = create_user_tokens(user_uuid)

    new_refresh_token = tokens["refresh_token"]

    usertoken_service.insert_user_token(
        UserTokenCreate(uuid=user_uuid, refresh_token=new_refresh_token)
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        expires=settings.refresh_token_expiration * 60,
        httponly=True,
        samesite="lax",
        secure=True,
    )

    return {"status": True, "message": "Success", "data": tokens}


@router.get("/auth/test", response_model=ResponseResult)
def test_api(
    user_uuid: Annotated[str, Depends(get_access_token_user_uuid)],
):
    """Protected test endpoint that only allows access using a valid access token"""

    return {"status": True, "message": "Success", "data": user_uuid}


@router.post("/logout", response_model=ResponseResult)
def logout_user(
    refresh_token: Annotated[Union[str, None], Cookie()] = None,
    access_token: Union[str, None] = Depends(get_access_token),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Endpoint to logout user"""
    usertoken_service = UserTokenService(db)
    blocklist_service = BlockListService(redis)

    usertoken_service.remove_user_token_by_token(refresh_token)

    if access_token:
        blocklist_service.add_token_to_blocklist(
            access_token,
            datetime.now() + timedelta(minutes=settings.access_token_expiration),
        )

    headers = {"Location": "/"}
    content = {"status": True, "message": "Successful Logout! 🛫", "data": None}
    response = JSONResponse(
        content=content,
        headers=headers,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )

    response.delete_cookie(key="refresh_token")

    return response
