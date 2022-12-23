# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from beecell.auth import SystemUser, DatabaseAuth, AbstractAuthDbManager
from beecell.db.manager import SqlManager
from beecell.simple import is_encrypted, decrypt_data
from beecell.tests.test_util import BeecellTestCase, runtest
import bcrypt


tests = [
    'test_login'
]

session = None
Base = declarative_base()


class User(Base):
    """User
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(50), unique=True)
    objid = Column(String(400))
    name = Column(String(100), unique=True)
    desc = Column(String(255))
    active = Column(Boolean())
    password = Column(String(150))

    def _check_password(self, password):
        # verifying the password
        if is_encrypted(self.password):
            res = (decrypt_data(self.password) == password.encode('utf-8'))
        else:
            res = bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
        return res


class AuthDbManager(AbstractAuthDbManager):
    def get_user(self, oid):
        global session
        query = session.query(User).filter_by(name=oid)
        return query.first()

    def verify_user_password(self, user, password):
        # verifying the password
        res = user._check_password(password)
        return res


class DbAuthTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

        self.manager = SqlManager(1, self.conf('authdb.conn'), connect_timeout=self.conf('authdb.timeout'))
        self.manager.create_simple_engine()
        self.auth_provider = DatabaseAuth(AuthDbManager, self.manager, SystemUser)
        self.user = self.conf('authdb.user')
        self.password = self.conf('authdb.pwd')

    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_login(self):
        global session
        session = self.manager.get_session()
        user = self.auth_provider.login(self.user, self.password)
        self.logger.debug(user)
        self.manager.release_session(session)


if __name__ == '__main__':
    runtest(DbAuthTestCase, tests)
