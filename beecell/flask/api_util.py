# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte

import json
from bson import BSON
from flask import request


def get_error(exception, code, data, mime='json'):
    error = {'status': 'error', 'api': request.path, 'exception': exception, 
             'code': str(code), 'data': str(data)}
    
    if mime == 'json':
        return json.dumps(error)
    elif mime == 'bson':
        return BSON.encode(error)

    
def get_response(data, mime='json'):
    res = {'status': 'ok', 'data': data}
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
            appname = 'beehive'
    elif request.method == 'GET':
        appname = request.args.get('app', 'beehive')
    return appname
