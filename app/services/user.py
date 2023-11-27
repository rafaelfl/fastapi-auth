"""Service for handling user authentication tasks"""
from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from passlib.context import CryptContext
from app.db.models import UserModel
from app.schemas.user import UserCreate, User, UserSignIn
from app.services.usertoken import UserTokenService
from app.utils.settings import settings
from app.utils.auth import decode_user_uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """User service class for handling user related JWT and database connections"""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate):
        """Create user use case method"""
        try:
            db = self.db

            db_user = UserModel(
                username=user.username,
                password=pwd_context.hash(user.password),
                name=user.name,
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            user_result = User(
                uuid=db_user.uuid,
                username=db_user.username,
                created_at=db_user.created_at,
                name=db_user.name,
            )

            return user_result
        except IntegrityError as err:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists"
            ) from err

    def signin(self, user_signin: UserSignIn):
        """User signin use case method"""
        db = self.db

        try:
            db_user = (
                db.query(UserModel)
                .filter(UserModel.username == user_signin.username)
                .one()
            )

            if not pwd_context.verify(user_signin.password, db_user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                )
            return str(db_user.uuid)

        except NoResultFound as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            ) from err

    def refresh_user_token(self, refresh_token: str):
        """Refresh tokens use case method"""
        db = self.db
        usertoken_service = UserTokenService(db)

        if refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No refresh token available",
            )

        user_uuid = decode_user_uuid(refresh_token, settings.refresh_token_private_key)

        try:
            # look for a valid refresh token
            usertoken = usertoken_service.find_usertoken(refresh_token)

            # in case a (valid) refresh token arives here but it is not in the database
            # (i.e., someone else used it), force the sign-in from all devices again
            if usertoken is None:
                print(
                    f"The refresh token sent from {user_uuid} could be used in another\
                      device. All devices were signed out."
                )
                usertoken_service.remove_all_user_tokens_by_uuid(user_uuid)

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Reusing rotated refresh token is not allowed.\
                    Expiring all refresh tokens",
                )

            usertoken_service.remove_user_token_by_token(refresh_token)

            return user_uuid
        except SQLAlchemyError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from err
