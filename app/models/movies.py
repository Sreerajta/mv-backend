
#cassandra tables storing movie data
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns
import uuid

#TODO:if this was to be used for real change partition key to something that is "useful" for partition ...
class MovieModel(Model):
    id      = columns.UUID(primary_key=True, default=uuid.uuid4) #TODO:change from uuid to hash(title+year)
    rating    = columns.Float()
    votes     = columns.BigInt(default=0)
    title     = columns.Text(required=False)
    plot     = columns.Text(required=False)
    genres   = columns.Text(required=False)
    poster   = columns.Text(required=False)

class UpvotesModel(Model):
    user_id = columns.Text(primary_key=True)
    movie_id = columns.UUID(primary_key=True, clustering_order="DESC") #TODO:change from uuid to hash(title+year)

class Timelines(Model):
    name = columns.Text(primary_key=True)
    movie_id = columns.UUID(primary_key=True,clustering_order="DESC")  #TODO:change from uuid to hash(title+year)
    rating    = columns.Float()
    votes     = columns.BigInt(default=0)
    title     = columns.Text(required=False)
    plot     = columns.Text(required=False)
    genres   = columns.Text(required=False)
    poster   = columns.Text(required=False)

class GenreToTimelineMappings(Model):
    genre = columns.Text(primary_key=True)
    timeline_name = columns.Text()
