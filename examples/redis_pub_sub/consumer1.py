'''
Created on Nov 27, 2017

@author: darkbk
'''
import time
import redis
queue = u'queue1'

r = redis.StrictRedis(host=u'10.102.91.23', port=6379, db=0)
p = r.pubsub(ignore_subscribe_messages=True)
p.subscribe(queue)

while True:
    message = p.get_message()
    if message:
        print queue, message
        # do something with the message
        time.sleep(0.05)  # be nice to the system :)