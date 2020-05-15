from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app import models,schemas

from app.utils import auth as authUtils

userModel = models.users.User
userSchema = schemas.users


def get_user(db: Session, user_id: int):
    return db.query(userModel).filter(userModel.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(userModel).filter(userModel.email == email).first()

def get_user_by_email_auth(db: Session, email: str):
    return db.query(userModel).filter(userModel.email == email).first()

def create_user(db: Session, user: userSchema.UserCreate):
    hashed_password = authUtils.get_password_hash(user.password)
    db_user = userModel(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user