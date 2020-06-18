from datetime import datetime, timedelta
from sqlalchemy.orm import Session

import jwt
from fastapi import Depends, FastAPI, HTTPException, status

from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext


from app.models import users as userModels
from app.schemas import users as userSchema
from app.schemas import auth as authSchema
from app.utils import users as userUtils
import global_config

userModel = userModels.User

UserInDB = userSchema.UserInDB
TokenData = authSchema.TokenData
User = userSchema.User

SECRET_KEY = global_config.jwt["SECRET_KEY"]
ALGORITHM = global_config.jwt["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = global_config.jwt["ACCESS_TOKEN_EXPIRE_MINUTES"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

app = FastAPI()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db:Session, email: str):
        user = userUtils.get_user_by_email_auth(db,email)
        return user


def authenticate_user(db:Session, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user



def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(db:Session,token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except PyJWTError:
        raise credentials_exception
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user



async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

