from sqlalchemy.orm import Session

from app import models,schemas

userModel = models.users.User
userSchema = schemas.users


def get_user(db: Session, user_id: int):
    return db.query(userModel).filter(userModel.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(userModel).filter(userModel.email == email).first()

def create_user(db: Session, user: userSchema.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed" #TODO  do hashing
    db_user = userModel(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user