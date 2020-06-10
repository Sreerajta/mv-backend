
from app.connections.sql import SessionLocal,engine
from cassandra.cqlengine.management import sync_table
from . import movies
from . import users as user_model

def sync_models():
    user_model.Base.metadata.create_all(bind=engine)
    sync_table(movies.MovieModel)
    sync_table(movies.UpvotesModel)