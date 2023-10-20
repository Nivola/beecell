# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

from beecell.db import QueryError
from .base import AuthError, AbstractAuth


class DatabaseAuth(AbstractAuth):
    def __init__(self, auth_manager, conn_manager, user_class):
        """Database authentication manager

        :param auth_manager: authentication manager. A class that extend beecell.auth.model.AuthManager and implement at
            least two method 'get_user' and 'verify_user_password'
        :param conn_manager: database connection manager. Instance of a class that extend
            'beecell.db.manager.ConnectionManager' and implement at least two method 'get_session' and 'release_session'
        :param user_class: flask_login user class
        """
        super(DatabaseAuth, self).__init__(user_class)

        self.auth_manager_class = auth_manager
        self.conn_manager = conn_manager

    def __str__(self):
        return "<DatabaseAuth provider:'%s', manager:'%s', user_class='%s'>" % (
            self.auth_manager_class,
            self.conn_manager.engine,
            self.user_class,
        )

    def login(self, username, password, *args, **kvargs):
        """Login a user

        :param username: user name
        :param password: user password
        :return: instance of user_class
        """
        self.logger.debug("Login user: %s" % username)

        # open database session
        session = self.conn_manager.get_session()
        auth_manager = self.auth_manager_class(session=session)
        self.logger.debug("Authentication manager: %s" % auth_manager.__module__)

        # verify that user exists in the db
        try:
            db_user = auth_manager.get_user(username)
        except (IndexError, QueryError) as ex:
            self.logger.error(ex)
            # release database session
            self.conn_manager.release_session(session)
            raise AuthError("", "User %s was not found" % username, code=5)

        if db_user == None:
            self.logger.error("Invalid credentials")
            # release database session
            self.conn_manager.release_session(session)
            raise AuthError("", "Invalid credentials", code=1)

        if db_user.active is not True:
            self.logger.error("User is disabled")
            # release database session
            self.conn_manager.release_session(session)
            raise AuthError("", "User is disabled", code=2)

        # authenticate user
        try:
            res = auth_manager.verify_user_password(db_user, password)
        except Exception as ex:
            self.logger.error(ex)
            # release database session
            self.conn_manager.release_session(session)
            raise AuthError("", "Invalid credentials", code=1)

        if not res:
            self.logger.error("Wrong password")
            # release database session
            self.conn_manager.release_session(session)
            raise AuthError("", "Wrong password", code=4)

        # create final user object
        user = self.user_class(db_user.uuid, username, password, True)

        # release database session
        self.conn_manager.release_session(session)

        self.logger.debug("Login succesfully: %s" % user)

        return user
