'''
Created on Oct 18, 2013

@author: darkbk
'''
from time import time
import logging
from multiprocessing import current_process
from threading import current_thread
from functools import wraps
from beecell.simple import id_gen, get_member_class

def watch(func):
    """Decorator function used to capture elapsed time.
    Configure 'watch' logger to save data."""
    @wraps(func)
    def inner(*args, **kwargs): #1
        logger = logging.getLogger(__name__)
        
        # get runtime info
        cp = current_process()
        ct = current_thread()
        
        # generate unique task id
        task_id = id_gen()
            
        # log start
        #classname = get_method_class(func)
        info = "%s:%s - %s:%s.%s - START" % (cp.ident, ct.ident, 
                                             func.__module__+'.'+get_member_class(args), 
                                             func.func_name, task_id)
        logger.info(info)
        
        # get start time
        start = time()
        
        # execute inner function
        ret = func(*args, **kwargs) #2
        
        # calculate elasped time
        elapsed = round(time() - start, 5)
        
        # log execution info in watch logger
        info = "%s:%s - %s:%s.%s - STOP - %s" % (cp.ident, ct.ident, 
                                                 func.__module__+'.'+get_member_class(args), 
                                                 func.func_name, task_id, elapsed)
        logger.info(info)
        return ret
    return inner

def watch_test(func):
    """Decorator function used to capture elapsed time.
    Configure 'test' logger to save data."""
    @wraps(func)
    def inner(*args, **kwargs): #1
        logging.getLogger('gibbon.test').info('========== %s ==========' % 
                                       (func.func_name))
        start = time()
        ret = func(*args, **kwargs) #2
        elapsed = round(time() - start, 4)
        logging.getLogger('gibbon.test').info("========== %s ========== : %ss\n" % 
                                       (func.func_name, elapsed))
        return ret
    return inner

class Timer(object):
    """Simple class to use when you need to measure elapsed time
    """
    startTime = 0
    
    def __init__(self):
        self.startTime = time()
    
    def restart(self):
        self.startTime = time()
    
    def elapsed(self):
        temp = time()
        #stop = round(temp - self.startTime, 3)
        stop = temp - self.startTime
        self.startTime = temp
        return stop
    
    def print_elapsed(self, message):
        elapsed = self.elapsed()
        print("%s - %s s" % (message, elapsed))