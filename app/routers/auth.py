"""Endpoints for authentication"""
from typing import Annotated, Union
from fastapi import APIRouter, Cookie, HTTPException, Response, Depends, status
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.schemas.response_result import ResponseResult
from app.schemas.user import UserCreate, UserSignIn
from app.utils.settings import settings
from app.utils.auth import get_access_token_user_uuid
from app.utils.jwt import create_user_tokens
from app.usecases.user import UserUseCase

router = APIRouter()


@router.post("/register", response_model=ResponseResult)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Endpoint for registering a new user"""
    user_usecase = UserUseCase(db)

    result_user = user_usecase.create_user(user)
    return {"status": True, "message": "Success", "data": result_user}


@router.post("/login", response_model=ResponseResult)
def login_user(
    user_signin: UserSignIn, response: Response, db: Session = Depends(get_db)
):
    """Endpoint for performing a username/password login"""
    user_usecase = UserUseCase(db)

    user = user_usecase.signin(user_signin)

    tokens = create_user_tokens(user)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        expires=settings.refresh_token_expiration * 60,
        httponly=True,
        samesite="lax",
        secure=True,
    )
    return {"status": True, "message": "Success", "data": tokens}


@router.post("/refresh", response_model=ResponseResult)
def refresh_tokens(
    response: Response,
    refresh_token: Annotated[Union[str, None], Cookie()] = None,
    db: Session = Depends(get_db),
):
    """Endpoint for refreshing an expired access token"""
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token available",
        )

    user_usecase = UserUseCase(db)

    user = user_usecase.refresh_user_token(refresh_token)

    tokens = create_user_tokens(user)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        expires=settings.refresh_token_expiration * 60,
        httponly=True,
        samesite="lax",
        secure=True,
    )
    return {"status": True, "message": "Success", "data": tokens}


@router.get("/auth/test", response_model=ResponseResult)
def test_api(user_uuid: Annotated[str, Depends(get_access_token_user_uuid)]):
    """Protected test endpoint that only allows access using a valid access token"""
    return {"status": True, "message": "Success", "data": user_uuid}
