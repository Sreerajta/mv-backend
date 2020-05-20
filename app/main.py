from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from .schemas import users


from .models import movies
from .models import sync_all
from .routers import users,movies
from .connections import cassandra_db
import global_config

cassandra_db.setup_cassandra_connection()

sync_all.sync_models()

app = FastAPI()


origins = [
    "http://localhost:3000",
   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(movies.router)

