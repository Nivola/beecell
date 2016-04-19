import sys
import os
path = os.path.dirname(__file__)
sys.path.append(path+'/c/lib/python2.7/site-packages')
import Extest

def fib(x):
    return Extest.fib(x)

def fib2(x):
    return Extest.fib2(x)

def fac(x):
    if (x < 2): return 1
    return Extest.fac(x)

def c_fib_multi(value):
    res = 0
    for i in xrange(0,value):
        res += fib(i)
    return res

def c_fib2_multi(value):
    res = 0
    for i in xrange(0,value):
        res += fib2(i)
    return res