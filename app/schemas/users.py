from typing import List

from pydantic import BaseModel

class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    genre_combo: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class UserInDB(User):
    hashed_password: str