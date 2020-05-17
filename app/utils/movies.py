
import requests
from datetime import datetime
from app.models import movies as movie_model
import global_config
from cassandra.query import SimpleStatement
from app.schemas import movies as movieSchema 

MovieModel = movie_model.MovieModel


def add_movie(movie_dict):
    MovieModel.create(rating = movie_dict['imdbRating'], created_at=datetime.now(),title=movie_dict['Title'],plot = movie_dict['Plot'],genres = movie_dict['Genre'].split())

def get_movie_from_omdb(movie_name):
    url = "http://www.omdbapi.com/"
    req_params = {'t':movie_name , 'apikey':global_config.api_keys['omdb']}
    r = requests.get(url= url, params = req_params)
    return r.json()



def get_movies_from_db (db_session,paging_state):
    query = 'SELECT * from movie_model'
    statement = SimpleStatement(query, fetch_size=3)
    if paging_state:
        results = db_session.execute(statement, paging_state = paging_state)
    else:
        results = db_session.execute(statement)
    print(results.paging_state)
    response_dict = {
        'paging_state':results.paging_state,
        'has_more_pages':results.has_more_pages,
        'result_list':[]
        }
    count = 0 #else the resultSet will autopage
    for row in results:
        if count < 3:
            response_dict['result_list'].append({
                'title': row['title'],
                'plot': row['plot'],
                'rating':row['rating'],
                'genres':list(row['genres'])
            })
            count += 1
    return response_dict


        