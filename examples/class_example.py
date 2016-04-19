# -*- coding: utf-8 -*-
'''
Created on Feb 11, 2015

@author: darkbr
'''
from gibbonutil.simple import str2uni

class prova(object):
    def __getattr__(self, name):
        return None

pp = prova()

print pp
print pp.ciao
a = 'ciaoé'
b = u'ciaoé'
a
b
print str2uni(a), type(str2uni(a))
print str2uni(b), type(str2uni(b))