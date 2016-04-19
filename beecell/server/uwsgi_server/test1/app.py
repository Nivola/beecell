'''
Created on Jan 19, 2013

@author: io
'''
import sys
import time
import traceback
import random

from gibbon.util.uwsgi_wrapper import uwsgi_util
from gibbon.util.server.wsgi_server.test1.log_config import severLogger
from gibbon.util.server.wsgi_server.test1.task import int_cpu_function
from gibbon.util.server.wsgi_server.test1.task import ext_cpu_function
from gibbon.util.server.wsgi_server.test1.varaibles import *
from gibbon.util.flask.decorators import jsonp
#from gibbon.util.monitor.resource import info
#from gibbon.util.monitor.resource import stats

import gibbon.util.monitor.resource as resource


from flask import Flask
from flask import request
application = Flask(__name__)

'''
def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    #portal2.task.a_long_task.spool(foo='bar')
    mule_test()
    return "Hello World"
'''

def tester(func, ext):
    start = time.time()
    wid = uwsgi_util.worker_id()
    mid = uwsgi_util.mule_id()
    req = random.randint(0,10000000)
    severLogger.debug("req:%s, worker:%s, mule:%s - START" % (req, wid, mid))
    
    res = []
    value = 25
    
    uwsgi_util.queue_set(wid, 'START')
    func(wid, req, value)
    
    # block worker until mule function return value in workers common queue at wordker_id position
    # 
    if ext == True:
        while(True):
            if round(time.time() - start, 3) >= timeout:
                severLogger.debug("req:%s, worker:%s, mule:%s - TIMEOUT" % (req, wid, mid))
                break
            if uwsgi_util.queue_get(wid) == 'STOP':
                break
    
    elapsed = round(time.time() - start, 5)
    
    severLogger.debug("req:%s, worker:%s, mule:%s - STOP - %s" % (req, wid, mid, elapsed))
    #return ','.join(res)
    return 'hello'

@application.route('/ext')
def test_ext_func():
    """
    Sync blocked socket with external cpu function
    """
    try:
        return tester(ext_cpu_function, True)
    except:
        severLogger.error(traceback.format_exc())
        
@application.route('/int')
def test_int_func():
    """
    Sync blocked socket with internal cpu function
    """    
    try:
        return tester(int_cpu_function, False)
    except:
        severLogger.error(traceback.format_exc())

@application.route('/info')
@jsonp
def info():
    try:
        active = request.args.get('active', '')
        
        if active != '':
            uwsgi_util.cache_update('info_status', active)
        return resource.info()
    except Exception as ex:
        severLogger.error(traceback.format_exc())

@application.route('/reload')
def reload():
    uwsgi_util.reload()

@application.route('/stats')
def stats():
    try:
        return resource.stats()
    except Exception as ex:
        severLogger.error(traceback.format_exc())

@application.route('/procs_tree')
def procs_tree():
    try:
        return resource.procs_tree()
    except Exception as ex:
        severLogger.error(traceback.format_exc())

        
'''        
@application.route('/info')
def resource(active):
    return info()
'''

def start_server():
    print "Start wsgi application"
    random.seed()
    application.run()
    
if __name__ == '__main__':
    start_server()