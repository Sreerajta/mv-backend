import json
import redis
import greenstalk
import uuid

from cassandra.cqlengine import connection
from cassandra.query import SimpleStatement
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

def setup_cassandra_connection():
    connection.setup(['127.0.0.1'], "default_keyspace", protocol_version=3)
    

def unregister_cassandra_connection():
    connection.unregister_connection('default_cas')

def get_cassandra_session():
    cluster = Cluster(protocol_version=3)
    session = cluster.connect()
    session.set_keyspace("default_keyspace")
    session.row_factory = dict_factory
    return session

cassandra_session = get_cassandra_session()

r = redis.Redis(host='localhost', port=6379, db=0)
queue = greenstalk.Client(host='127.0.0.1', port=11305)
queue.watch('timeline_votes_produce')
queue2 = greenstalk.Client(host='127.0.0.1', port=11305)
queue2.use('timeline_votes_consumer')

######## MOCK FUNCTIONS
genre_to_timeiline_mappings = {
    'Action':["Action,Comedy"],
    'Comedy':["Action,Comedy"],
    'Drama':["Drama","Drama,Fantasy"],
    'Fantasy':["Drama,Fantasy"],
    'Family':[],
    'Animation':[],
    'Short':[],
    'Adventure':["Adventure"],
    'Sci-Fi':["Sci-Fi"]
}

def get_timelines_by_genre(genre:str):
    return genre_to_timeiline_mappings[genre]
########


def get_movie_genres(movie_id:str):
    movie_id_uuid = uuid.UUID(movie_id)
    query = 'SELECT genres FROM movie_model WHERE id=%s LIMIT 1'
    genres = cassandra_session.execute(query,[movie_id_uuid])
    return genres

def get_timelines_for_genres(genres:list):
    timelines_list = []
    for genre in genres:
        timelines = get_timelines_by_genre(genre.strip())
        for timeline in timelines:
            if timeline not in timelines_list:
                timelines_list.append(timeline)
    return timelines_list

def create_timeline_vote_jobs(movie_id:str):
    movie_genres = get_movie_genres(movie_id)
    movie_genres = movie_genres.one()
    movie_genres = movie_genres['genres'].split(',')
    timelines = get_timelines_for_genres(movie_genres)
    for timeline in timelines:        
        timeline_vote = {"timeline":timeline,
                         "movie":movie_id}
        queue2.put(json.dumps(timeline_vote))
    

while(True):
    job = queue.reserve()
    movie_id = job.body
    create_timeline_vote_jobs(movie_id)
    queue.delete(job)