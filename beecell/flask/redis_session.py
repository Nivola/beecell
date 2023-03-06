# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

import pickle
import logging
from datetime import timedelta
from uuid import uuid4
from redis import Redis
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin


class RedisSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    serializer = pickle
    session_class = RedisSession
    session_duration = 1800

    def __init__(self, redis=None, prefix="session:"):
        self.logger = logging.getLogger(
            self.__class__.__module__ + "." + self.__class__.__name__
        )

        if redis is None:
            redis = Redis()

        self.redis = redis
        self.prefix = prefix

    def generate_sid(self):
        return str(uuid4())

    def get_redis_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return self.session_duration

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
        val = self.redis.get(self.prefix + sid)
        if val is not None:
            data = self.serializer.loads(val)
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            self.redis.delete(self.prefix + session.sid)
            if session.modified:
                response.delete_cookie(app.session_cookie_name, domain=domain)
            return

        redis_exp = self.get_redis_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.setex(self.prefix + session.sid, redis_exp, val)
        response.set_cookie(
            app.session_cookie_name,
            session.sid,
            expires=cookie_exp,
            httponly=True,
            domain=domain,
        )

    def save_session2(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            if session.modified:
                response.delete_cookie(
                    app.session_cookie_name, domain=domain, path=path
                )
            return
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        redis_exp = self.get_redis_expiration_time(app, session)
        expires = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.setex(self.prefix + session.sid, redis_exp, val)

        response.set_cookie(
            app.session_cookie_name,
            val,
            expires=expires,
            httponly=httponly,
            domain=domain,
            path=path,
            secure=secure,
        )

    def remove_session(self, session, sid=None):
        if session is None:
            self.redis.delete(self.prefix + sid)
        else:
            self.redis.delete(self.prefix + session.sid)

    def get_session(self, sid):
        val = self.redis.get(self.prefix + sid)
        if val is not None:
            data = self.serializer.loads(val)
            return data
        else:
            return None

    def list_sessions(self):
        sessions = []
        for key in self.redis.keys("%s*" % self.prefix):
            val = self.redis.get(key)
            data = self.serializer.loads(val)
            data["ttl"] = self.redis.ttl(key)
            data["sid"] = key[len(self.prefix) :]
            sessions.append(data)

        return sessions
