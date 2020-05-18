# A simple api written in python/fastapi that serves movies from a cassandra table.

###### 1)clone the repo
###### 2)rename sample_global_config_.py to global_config.py (or run create_initial config) and edit the file to add cassandra hosts  keyspace name, omdb api key and secret key for jwt generation.
###### 3)install requirements using pip
###### 4)run the app 
- uvicorn app.main:app 
