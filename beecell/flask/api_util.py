'''
Created on May 23, 2014

@author: darkbk
'''
import json
from bson import BSON
from flask import request

def get_error(exception, code, data, mime='json'):
    error = {'status':'error', 'api':request.path, 'exception':exception, 
             'code':str(code), 'data':str(data)}
    
    if mime == 'json':
        return json.dumps(error)
    elif mime == 'bson':
        return BSON.encode(error)
    
def get_response(data, mime='json'):
    res = {'status':'ok', 'data':data}
    if mime == 'json':
        return json.dumps(res)
    elif mime == 'bson':
        return BSON.encode(res)

def get_mime():
    if request.method == 'POST':
        try:
            mime = request.form['mime']
        except:
            mime = 'json'
    elif request.method == 'GET':
        mime = request.args.get('mime', 'json')
    return mime

def get_app():
    if request.method == 'POST':
        try:
            appname = request.form['app']
        except:
            appname = 'cloudapi'
    elif request.method == 'GET':
        appname = request.args.get('app', 'cloudapi')
    return appname