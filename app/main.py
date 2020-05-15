from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy.orm import Session

from .schemas import users
from .connections.sql import SessionLocal,engine
from .models import users as userModel
from .routers import users



userModel.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)


