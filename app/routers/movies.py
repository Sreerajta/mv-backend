from fastapi import APIRouter, Depends, Header, HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from time import sleep

import app.schemas.movies as movieSchema
import app.utils.movies as movieUtils
import app.connections.cassandra_db as cassandra_db
from cassandra.query import SimpleStatement, ValueSequence,PreparedStatement
import jwt
import fnc

get_cassandra_session = cassandra_db.get_cassandra_session

router = APIRouter()

MovieRespone = movieSchema.MovieResponse


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

db_session = get_cassandra_session()






# def get_paging_state(response):
#         if 'paging_state' in response: 
#             return response['paging_state'] 
#         else: 
#             return '' 

#################################################################################################################################
#WARNING: paging state should be cached in server side per user session ? , since it can be forged to access different partitions
#################################################################################################################################



@router.get("/getMovies", response_model=MovieRespone)
def get_movies(paging_state:int=1, token: str = Depends(oauth2_scheme)):
    token_decoded = jwt.decode(token,"jkasgfjasgfkjgas9867876jukfbas54536asf4fufy7",algorithms=['HS256']) #TODO:read from config
    user = token_decoded['sub']
    response = movieUtils.get_movies_from_db2(db_session,user,paging_state)
    # response = movieUtils.get_movies_from_db(db_session,paging_state)
    return {
        'movies':response['result_list'],
        'has_more_pages':response['has_more_pages'],
        'paging_state': paging_state +1         
    }


@router.get("/upvoteMovie")
def upvote_movie(movie_id:str,token: str = Depends(oauth2_scheme)):
    print(token)
    token_decoded = jwt.decode(token,"jkasgfjasgfkjgas9867876jukfbas54536asf4fufy7",algorithms=['HS256']) #TODO:read from config
    user = token_decoded['sub']
    movieUtils.upvote_movie(user,movie_id)
    return True


@router.get("/test")
async def test_ids(paging_state:int=0,genre_filter:str='Action,Comedy', token:str = Depends(oauth2_scheme)):
    token_decoded = jwt.decode(token,"jkasgfjasgfkjgas9867876jukfbas54536asf4fufy7",algorithms=['HS256']) #TODO:read from config
    user = token_decoded['sub']
    response,counter,cache_pointer = await movieUtils.get_movies_from_db_temp(db_session,user,genre_filter,paging_state)
    return {
        'movies':response['result_list'],
        'has_more_pages':response['has_more_pages'],
        'paging_state': cache_pointer         
    }

@router.get("/dummy")
async def dummy():
    query = 'SELECT * FROM movie_model LIMIT 5'
    # statement = SimpleStatement(query)
    future = db_session.execute_async(query)
    def handle_success(rows):
        result = list(fnc.map({'id','genres'},rows))
        print(result)
        return result
    

    def handle_error(exception):
        print("Failed to fetch user info: %s", exception)
    
    future.add_callbacks(handle_success, handle_error)
    
    