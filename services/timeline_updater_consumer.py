import json
import redis
import greenstalk
import uuid

queue = greenstalk.Client(host='127.0.0.1', port=11305)
queue.watch('timeline_votes_consumer')




while(True):
    job = queue.reserve()
    job = json.loads(job.body)
    print(job)