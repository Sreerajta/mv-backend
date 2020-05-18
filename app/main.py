from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy.orm import Session


from .schemas import users


from .models import movies
from .models import sync_all
from .routers import users,movies
from .connections import cassandra_db

cassandra_db.setup_cassandra_connection()

sync_all.sync_models()

app = FastAPI()

app.include_router(users.router)
app.include_router(movies.router)

