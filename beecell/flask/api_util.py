# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2024 CSI-Piemonte

from bson import BSON
from flask import request, Request
from beecell.simple import jsonDumps


def get_remote_ip(request: Request):
    """Get a remote id

    :param request: request to do
    :return:  remote ip
    """
    try:
        try:
            # get remote ip when use nginx as balancer
            ipaddr = request.environ["HTTP_X_REAL_IP"]
        except:
            ipaddr = request.environ["REMOTE_ADDR"]

        return ipaddr
    except RuntimeError:
        return None


def get_error(exception, code, data, mime="json"):
    error = {
        "status": "error",
        "api": request.path,
        "exception": exception,
        "code": str(code),
        "data": str(data),
    }

    if mime == "json":
        return jsonDumps(error)
    elif mime == "bson":
        return BSON.encode(error)


def get_response(data, mime="json"):
    res = {"status": "ok", "data": data}
    if mime == "json":
        return jsonDumps(res)
    elif mime == "bson":
        return BSON.encode(res)


def get_mime():
    if request.method == "POST":
        try:
            mime = request.form["mime"]
        except:
            mime = "json"
    elif request.method == "GET":
        mime = request.args.get("mime", "json")
    return mime


def get_app():
    if request.method == "POST":
        try:
            appname = request.form["app"]
        except:
            appname = "beehive"
    elif request.method == "GET":
        appname = request.args.get("app", "beehive")
    return appname
