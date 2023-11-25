"""Service for managing generated usertoken"""
from sqlalchemy.orm import Session

from app.db.models import UserModel, UserTokenModel
from app.schemas.usertoken import UserToken, UserTokenCreate


class UserTokenService:
    """UserToken service class for handling usertoken database connections"""

    def __init__(self, db: Session):
        self.db = db

    def create_user_token(self, usertoken: UserTokenCreate):
        """Create a new usertoken record to store the current valid refresh token"""
        db = self.db

        db_usertoken = UserTokenModel(
            uuid=usertoken.uuid,
            refresh_token=usertoken.refresh_token,
        )

        db.add(db_usertoken)
        db.commit()
        db.refresh(db_usertoken)

        usertoken = UserToken(
            uuid=db_usertoken.uuid,
            refresh_token=db_usertoken.refresh_token,
            created_at=db_usertoken.created_at,
        )

        return usertoken

    def find_user_token(self, token: str):
        """Return a UserToken object found by a refresh token"""
        db = self.db

        db_usertoken = (
            db.query(UserTokenModel)
            .join(UserModel)
            .filter(UserTokenModel.refresh_token == token)
            .first()
        )

        if db_usertoken is None:
            return None

        usertoken = UserToken(
            uuid=db_usertoken.uuid,
            refresh_token=db_usertoken.refresh_token,
            created_at=db_usertoken.created_at,
        )

        return usertoken

    def remove_all_user_tokens_by_uuid(self, uuid: str):
        """Remove all UserToken records by UUID"""
        db = self.db

        db.query(UserTokenModel).filter_by(uuid=uuid).delete()

    def remove_user_token_by_token(self, token: str):
        """Remove the UserToken record by token"""
        db = self.db

        db.query(UserTokenModel).filter_by(refresh_token=token).delete()
