"""Use cases for handling user authentication tasks"""
from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound
from passlib.context import CryptContext
from db.models import UserModel
from schemas.user import UserCreate, User, UserSignIn
from utils.settings import settings
from utils.auth import decode_user_uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserUseCase:
    """Use case class for handling user tasks"""
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
                last_update=db_user.last_update,
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

            user_result = User(
                uuid=db_user.uuid,
                username=db_user.username,
                last_update=db_user.last_update,
                name=db_user.name,
            )

            return user_result

        except NoResultFound as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            ) from err

    def refresh_user_token(self, refresh_token: str):
        """Refresh tokens use case method"""
        db = self.db

        user_uuid = decode_user_uuid(refresh_token, settings.refresh_token_private_key)

        try:
            db_user = db.query(UserModel).filter(UserModel.uuid == user_uuid).one()

            user_result = User(
                uuid=db_user.uuid,
                username=db_user.username,
                last_update=db_user.last_update,
                name=db_user.name,
            )

            return user_result
        except NoResultFound as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from err