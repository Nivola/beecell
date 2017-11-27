'''
Created on Nov 24, 2017

@author: io
'''
from rediscluster import StrictRedisCluster
# Requires at least one node for cluster discovery. Multiple nodes is recommended.
startup_nodes = [{"host": "10.102.184.121", "port": "6379"},
                 {"host": "10.102.91.23", "port": "6379"},
                 {"host": "10.102.91.24", "port": "6379"}]

# Note: See note on Python 3 for decode_responses behaviour
rc = StrictRedisCluster(startup_nodes=startup_nodes, decode_responses=True)
print(rc.ping())
print(rc)
rc.set("foo", "bar")
print(rc.get("foo"))
print(rc.keys(u'fr'))