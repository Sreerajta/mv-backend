from fastapi import APIRouter, Depends, Header, HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta

from app import connections
import app.utils.users as userUtils
import app.schemas.users as userSchema
import app.schemas.auth as authSchema
import app.utils.auth as authUtils
import global_config

ACCESS_TOKEN_EXPIRE_MINUTES = global_config.jwt["ACCESS_TOKEN_EXPIRE_MINUTES"]


router = APIRouter()


get_db = connections.sql.get_db
authenticate_user = authUtils.authenticate_user
get_current_active_user = authUtils.get_current_active_user
create_access_token = authUtils.create_access_token

Token = authSchema.Token
User = userSchema.User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")



@router.post("/createUser")
def create_user(user: userSchema.UserCreate, db: Session = Depends(get_db)):
    db_user = userUtils.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return userUtils.create_user(db=db, user=user)


@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}




