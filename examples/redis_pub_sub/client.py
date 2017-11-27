'''
Created on Nov 27, 2017

@author: darkbk
'''
import redis

queues = [u'queue1', u'queue2']

r = redis.StrictRedis(host=u'10.102.91.23', port=6379, db=0)
for queue in queues:
    r.publish(queue, u'hello')