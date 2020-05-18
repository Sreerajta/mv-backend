from fastapi import APIRouter, Depends, Header, HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta

import app.schemas.movies as movieSchema
import app.utils.movies as movieUtils
import app.connections.cassandra_db as cassandra_db

get_cassandra_session = cassandra_db.get_cassandra_session

router = APIRouter()

MovieRespone = movieSchema.MovieResponse


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_paging_state(response):
        if 'paging_state' in response: 
            return response['paging_state'] 
        else: 
            return '' 

#################################################################################################################################
#WARNING: paging state should be cached in server side per user session ? , since it can be forged to access different partitions
#################################################################################################################################



@router.get("/getMovies", response_model=MovieRespone)
def get_movies(paging_state:str=None, token: str = Depends(oauth2_scheme)):
    db_session = get_cassandra_session()
    response = movieUtils.get_movies_from_db(db_session,paging_state)
    return {
        'movies':response['result_list'],
        'has_more_pages':response['has_more_pages'],
        'paging_state': get_paging_state(response)            
    }


    