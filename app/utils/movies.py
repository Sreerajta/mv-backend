
import requests
from datetime import datetime
from app.models import movies as movie_model
import global_config
from cassandra.query import SimpleStatement
from app.schemas import movies as movieSchema 
import uuid
from base64 import b64encode , b64decode
import re

DATA_FETCH_SIZE_MOVIE = 5


MovieModel = movie_model.MovieModel


def add_movie(movie_dict):
    MovieModel.create(rating = movie_dict['imdbRating'], created_at=datetime.now(),title=movie_dict['Title'],plot = movie_dict['Plot'],genres = movie_dict['Genre'].split())

def get_movie_from_omdb(movie_name):
    url = "http://www.omdbapi.com/"
    req_params = {'t':movie_name , 'apikey':global_config.api_keys['omdb']}
    r = requests.get(url= url, params = req_params)
    return r.json()



def get_movies_from_db (db_session,paging_state):
    query = 'SELECT * from movies_list'
    statement = SimpleStatement(query ,fetch_size=DATA_FETCH_SIZE_MOVIE)
    if paging_state:
        paging_state = b64decode(paging_state) 
        results = db_session.execute(statement, paging_state = paging_state)
    else:
        results = db_session.execute(statement)
    paging_state = results.paging_state
    response_dict = {
        'has_more_pages':True,
        'result_list':[]
        }
    if(paging_state):
          #b64encode the paging_state bytes object to be transmitted as part of response[not reccomended to send it to client]..
         response_dict.setdefault("paging_state", b64encode(results.paging_state))
    #count placed below since the resultSet object auto paginates  , wants to paginate in a RESTful way using the paging_state bytes object returned       
    count = 0 
    for row in results:
        if count < 5:        
            response_dict['result_list'].append({
                'title': row['title'],
                'plot': row['plot'],
                'rating':row['rating'],
                'genres':row['genres'],
                'poster':row['poster']
                })
            count += 1
        else:
            break
    return response_dict


        