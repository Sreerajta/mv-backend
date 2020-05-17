
from cassandra.cqlengine import connection
from global_config import cassandra_config

from cassandra.cluster import Cluster
from app.utils import movies
from cassandra.query import dict_factory




def setup_cassandra_connection():
    connection.setup(cassandra_config["hosts"], cassandra_config["default_keyspace"], protocol_version=3)
    

def unregister_cassandra_connection():
    connection.unregister_connection('default_cas')

def get_cassandra_session():
    cluster = Cluster(protocol_version=3)
    session = cluster.connect()
    session.set_keyspace('test_keyspace')
    session.row_factory = dict_factory
    # connection.register_connection('default_cas', session=session)
    return session
    

 


