"""Endpoints for authentication"""
from typing import Annotated, Union
from fastapi import APIRouter, Cookie, Response, Depends
from sqlalchemy.orm import Session
from depends import get_db
from schemas.response_result import ResponseResult
from schemas.user import UserCreate, UserSignIn
from utils.settings import settings
from usecases.user import UserUseCase
from utils.auth import get_current_user_uuid
from utils.jwt import create_user_tokens

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
def test_api(user_uuid: Annotated[str, Depends(get_current_user_uuid)]):
    """Protected test endpoint that only allows access using a valid access token"""
    return {"status": True, "message": "Success", "data": user_uuid}
