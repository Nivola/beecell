'''
Created on Jan 15, 2013

@author: io
'''
import sys
import time
from uwsgidecorators import *
from gibbon.util.uwsgi_wrapper import uwsgi_util
from gibbon.util.server.wsgi_server.test1.log_config import severLogger
from gibbon.util.mathlib.pylib import fib
from gibbon.util.monitor.resource import info
from gibbon.util.server.wsgi_server.test1.varaibles import *

def int_cpu_function(wid, req, value):
    res = fib(value)

@mulefunc
def ext_cpu_function(wid, req, value):
    start = time.time()
    mid = uwsgi_util.mule_id()
    severLogger.debug("req:%s, worker:%s, mule:%s - START" % (req, wid, mid))
    #time.sleep(2)
    res = fib(value)
    #print "[%s] mule result : %s" % (time.time(), res)
    # Put a binary string in slot 17.
    uwsgi_util.queue_set(wid, 'STOP')
    elapsed = round(time.time() - start, 5)
    severLogger.debug("req:%s, worker:%s, mule:%s - STOP - %s" % (req, wid, mid, elapsed))

'''
@timer(info_period, target='mule1')
def cron_func(signum):
    info_status = uwsgi_util.cache_get('info_status')
    print info_status
    if info_status == 'true':
        wid = uwsgi_util.worker_id()
        mid = uwsgi_util.mule_id()
        severLogger.debug("worker:%s, mule:%s - 1 second elapsed" % (wid, mid))
    else:
        pass
'''
'''

def hello_timer(num):
    print "2 seconds elapsed, signal %d raised" % num

def oneshot_timer(num):
    print "40 seconds elapsed, signal %d raised. You will never see me again." % num

uwsgi_util.register_signal(26, "mule1", hello_timer)

uwsgi_util.add_timer(26, 2) # never-ending timer every 2 seconds
'''


@rpc('helloworld')
def ciao_mondo_function():
    return "Hello World"

'''
@spool
def a_long_task(args):
    print(args)

@spool
def a_longer_task(args):
    print("longer.....")


@timer(3)
def three_seconds(signum):
  print("3 seconds elapsed")

@timer(10, target='spooler')
def ten_seconds_in_the_spooler(signum):
  print("10 seconds elapsed in the spooler")
'''
'''  
@mulefunc(3)
def on_three():
    print "I'm running on mule 3."
'''