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


r = redis.Redis(host='localhost', port=6379, db=0)
queue = greenstalk.Client(host='127.0.0.1', port=11305)
queue.watch('upvotes')

cassandra_session = get_cassandra_session()


def count_iterable(i):
    return sum(1 for e in i)

def update_movie_by_id(movie_id):
    r.zincrby('movies', 1, movie_id)

while(True):
    job = queue.reserve()
    job_json = json.loads(job.body)
    movie_id = job_json['movie_id']
    user_id = job_json['user']
    movie_id_uuid = uuid.UUID(movie_id)
    votes_query = 'SELECT user_id from upvotes_model WHERE user_id=%s and movie_id=%s'
    votes = cassandra_session.execute(votes_query,[user_id,movie_id_uuid])
    if count_iterable(votes) == 0:
        cur_value = r.zscore('movies',movie_id)
        upvote_query = """
            INSERT INTO upvotes_model (user_id,movie_id)
            VALUES (%s, %s)
            """
        cassandra_session.execute(upvote_query,[user_id,movie_id_uuid])
        new_vote = int(cur_value) + 1
        query = 'UPDATE movie_model SET votes=%s WHERE id=%s'
        cassandra_session.execute(query,[new_vote,movie_id_uuid])
        r.zincrby('movies', 1, movie_id)        
    queue.delete(job)   #TODO:bury/ put into failed queue instead of deleting if update fails