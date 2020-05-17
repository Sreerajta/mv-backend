
#cassandra table storing movie data
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns
import uuid

#TODO: change partition key
class MovieModel(Model):
    id      = columns.UUID(primary_key=True, default=uuid.uuid4)
    rating    = columns.Float(index=True)
    created_at      = columns.DateTime()
    title     = columns.Text(required=False)
    plot     = columns.Text(required=False)
    genres   = columns.Set(columns.Text)