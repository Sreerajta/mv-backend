
import requests
from datetime import datetime
from app.models import movies as movie_model
import global_config
from cassandra.query import SimpleStatement, ValueSequence,PreparedStatement
from app.schemas import movies as movieSchema 
import uuid
from base64 import b64encode , b64decode
import re
import json
import fnc

######
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
import greenstalk
queue = greenstalk.Client(host='127.0.0.1', port=11305) #edit here for beasntalk params MOVE THIS TO CONNECTIONS
queue.use('upvotes')
######

DATA_FETCH_SIZE_MOVIE = 5
USE_CACHE = True

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


# def get_top_movies_from_redis_timelines(timelines:list,count:int,page:int):
#     offset = (page-1) * count
#     res_set = r.zrange('movies', offset, offset+count-1, withscores=True,desc=True)
#     return res_set


def get_top_movies_from_redis(count:int,page:int):
    # offset = (page-1) * count
    offset = page
    res_set = r.zrange('movies', offset, offset+count-1, withscores=True,desc=True)
    return res_set

def get_movies_from_db2(db_session,user,paging_state):
    result_dict  = {
        'has_more_pages':True,
        'result_list':[]
        }
    top_movies = get_top_movies_from_redis(10,paging_state)
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


#demo function to filter from main list##########################################
def get_top_movies_from_redis_timeline(timeline_key:str,count:int,page:int):
    # offset = (page-1) * count
    offset = page + 1
    res_set = r.zrange(timeline_key, offset, offset+count-1, withscores=True,desc=True)
    return res_set



def get_timeline_key(genre_filter:list):
    genre_list = sorted(genre_filter)
    genre_list = ','.join(genre_list)
    timeline_key = 'timeline:'+genre_list
    return timeline_key

def cache_exists(timeline_key:str):
    timeline_status = r.get(timeline_key)
    if timeline_status == None:
        return 'false'
    if timeline_status == '0':
        return 'processing'
    elif timeline_status == '1':
        return 'true'


async def get_data_from_main_db(db_session,user,movie_ids):
    result_dict  = {
        'has_more_pages':True,
        'result_list':[]
        }
    query = 'SELECT * FROM movie_model WHERE id IN %s'
    statement = SimpleStatement(query)
    results_future = db_session.execute_async(statement,parameters=[ValueSequence(movie_ids)])
    user_upvote_query = 'SELECT movie_id FROM upvotes_model WHERE user_id=%s and movie_id IN %s'
    user_upvotes_statement =SimpleStatement(user_upvote_query)
    user_upvotes_future = db_session.execute_async(user_upvotes_statement,[user,ValueSequence(movie_ids)])
    user_upvoted_movies =[]
    user_upvotes = user_upvotes_future.result()
    results = results_future.result()
    for row in user_upvotes:
        user_upvoted_movies.append(row['movie_id'])
    result_dict['result_list'] = list(map(lambda result: {'title':result['title'],'plot':result['plot'],'rating':result['rating'],
            'genres':result['genres'],
            'poster':result['poster'],
            'votes':result['votes'],
            'id':result['id'],'user_voted':if_user_voted(user_upvoted_movies,result['id'])},results))
    return result_dict

async def get_movies_from_db_temp(db_session,user,genre_filter,paging_state):
    has_cache = False
    if USE_CACHE:
        timeline_key = get_timeline_key(genre_filter)
        cache_status = cache_exists(genre_filter)
        if cache_status == 'false':
            print('===no cache')#create cache lookup entry with status 0/processing and return
        elif cache_status =='processing':
            print('required_cache_under_processing')
        elif cache_status =='true':
            has_cache = True    

    counter = 0
    cache_pointer = paging_state
    result_ids = []
    if has_cache:
        res = get_top_movies_from_redis_timeline(timeline_key,10,paging_state)
    else:
        res = get_top_movies_from_redis(1000,paging_state)
    top_ids = []
    for movie in res:
        top_ids.append(movie[0])
    
    if has_cache:
        for i in range(len(top_ids)):
            result_ids.append(uuid.UUID(top_ids[i].decode("utf-8")))
        result_dict = await get_data_from_main_db(db_session,user,result_ids)
        return result_dict,counter,cache_pointer
    else:
        genre_filter = genre_filter.split(',')
        pipe = r.pipeline()
        for top_id in top_ids:
            pipe.hmget(top_id,genre_filter)
        genre_exists = pipe.execute()
        
        for i in range(len(top_ids)):
            cache_pointer +=1
            if b'1' in genre_exists[i]:
                result_ids.append(uuid.UUID(top_ids[i].decode("utf-8")))
                counter +=1 
                if counter == 10:
                    result_dict = await get_data_from_main_db(db_session,user,result_ids)
                    return result_dict,counter,cache_pointer  
        result_dict = await get_data_from_main_db(db_session,user,result_ids)
        return result_dict,counter,cache_pointer
    
    # return result_ids,counter,cache_pointer


######################################################################################################################    




def upvote_movie(user,movie_id):
    vote = {"user":user,
            "movie_id":movie_id}    
    vote_serialised = json.dumps(vote)
    print(vote_serialised)
    queue.put(vote_serialised)
        