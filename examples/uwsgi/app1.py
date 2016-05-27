'''
Created on May 16, 2015

@author: darkbk
'''
import sys, os
import gevent
from gevent import monkey
monkey.patch_all()

from flask import Flask, request
app = Flask(__name__)

@app.route("/")
def hello():
    return 'hello'