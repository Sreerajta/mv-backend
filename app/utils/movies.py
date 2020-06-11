
import requests
from datetime import datetime
from app.models import movies as movie_model
import global_config
from cassandra.query import SimpleStatement, ValueSequence
from app.schemas import movies as movieSchema 
import uuid
from base64 import b64encode , b64decode
import re
import json

######
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
import greenstalk
queue = greenstalk.Client(host='127.0.0.1', port=11305) #edit here for beasntalk params MOVE THIS TO CONNECTIONS
queue.use('upvotes')
######

DATA_FETCH_SIZE_MOVIE = 5


MovieModel = movie_model.MovieModel


def add_movie(movie_dict):
    MovieModel.create(rating = movie_dict['imdbRating'], created_at=datetime.now(),title=movie_dict['Title'],plot = movie_dict['Plot'],genres = movie_dict['Genre'].split())

def get_movie_from_omdb(movie_name):
    url = "http://www.omdbapi.com/"
    req_params = {'t':movie_name , 'apikey':global_config.api_keys['omdb']}
    r = requests.get(url= url, params = req_params)
    return r.json()


def if_user_voted(user_upvoted_movies,movie_id):
    if movie_id in user_upvoted_movies:
        return 'true'
    else:
        return 'false'


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


def get_top_movies_from_redis(count:int):
    res_set = r.zrange('movies', 0, count, withscores=True,desc=True)
    return res_set

def get_movies_from_db2(db_session,user):
    result_dict  = {
        'has_more_pages':True,
        'result_list':[]
        }
    top_movies = get_top_movies_from_redis(10)
    top_ids = []
    for movie in top_movies:
        top_ids.append(uuid.UUID(movie[0].decode("utf-8")))
    query = 'SELECT * FROM movie_model WHERE id IN %s'
    statement = SimpleStatement(query)
    results = db_session.execute(statement,parameters=[ValueSequence(top_ids)])
    user_upvote_query = 'SELECT movie_id FROM upvotes_model WHERE user_id=%s and movie_id IN %s'
    user_upvotes_statement =SimpleStatement(user_upvote_query)
    user_upvotes = db_session.execute(user_upvotes_statement,[user,ValueSequence(top_ids)])
    user_upvoted_movies =[]
    for row in user_upvotes:
        user_upvoted_movies.append(row['movie_id'])
    for row in results:
        result_dict['result_list'].append({
                'title': row['title'],
                'plot': row['plot'],
                'rating':row['rating'],
                'genres':row['genres'],
                'poster':row['poster'],
                'votes':row['votes'],
                'id':row['id'],
                'user_voted':if_user_voted(user_upvoted_movies,row['id'])
                })
    return result_dict


def upvote_movie(user,movie_id):
    vote = {"user":user,
            "movie_id":movie_id}    
    vote_serialised = json.dumps(vote)
    queue.put(vote_serialised)
        