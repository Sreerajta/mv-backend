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

db_session = get_cassandra_session()


import fnc
from functools import partial

query = 'SELECT * FROM movie_model LIMIT 5'
future = db_session.execute_async(query)
result = future.result()
result_mapped = partial(fnc.map,{'id'})
get_res = fnc.compose(result_mapped,set)
res = get_res(result)
print(res)





