from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app import controllers,schemas,connections

router = APIRouter()

userController = controllers.users
userSchema = schemas.users 
get_db = connections.sql.get_db

@router.post("/createUser")
def create_user(user: userSchema.UserCreate, db: Session = Depends(get_db)):
    db_user = userController.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return userController.create_user(db=db, user=user)