# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

import logging
from flask_login import UserMixin
from beecell.perf import watch
from beecell.db import TransactionError, QueryError


class SystemUser(UserMixin):
    """System user returned after authentication. Use this with flask_login. 
    """    
    confirmed_at = None
    last_login_at = None
    current_login_at = None
    last_login_ip = None
    current_login_ip = None
    login_count = None
    
    def __init__(self, uid, email, password, active, login_ip=None, domain=None):
        self.logger = logging.getLogger(self.__class__.__module__ + u'.' + self.__class__.__name__)
        
        self.id = uid
        self.email = email
        self.password = password
        self.active = active
        self.domain = domain
        self._roles = None
        self._perms = None
        self._attrib = None
        self.current_login_ip = login_ip
        
        self.logger.debug(u'Create flask_login user instance: %s, %s' % (uid, email))

    def __str__(self):
        return u'<SystemUser id: %s, name: %s, active: %s ip= %s>' % \
               (self.id, self.email, self.active, self.current_login_ip)

    def get_dict(self):
        return {
            u'id': self.id,
            u'name': self.email,
            u'domain': self.domain,
            u'active': self.active,
            u'roles': self._roles,
            u'perms': self._perms
        }

    def set_groups(self, groups):
        self._groups = groups        

    def get_groups(self):
        return self._groups          

    def set_attributes(self, attrib):
        self._attrib = attrib  

    def get_attributes(self):
        return self._attrib

    def set_roles(self, roles):
        self._roles = roles

    def get_roles(self):
        return self._roles

    def set_perms(self, perms):
        self._perms = perms

    def get_perms(self):
        return self._perms


class AuthError(Exception):
    """Authentication provider exception.
    """
    def __init__(self, info, desc, code=None):
        """Authentication provider exception.

        code:
        1 - Invalid credentials
        2 - User is disabled
        3 - Password is expired
        4 - Wrong password
        5 - User does not exist
        7 - Connection error
        9 - Undefined
        10 - Domain error

        wrong password, wrong user:
            info: 80090308: LdapErr: DSID-0C0903C5, comment: AcceptSecurityContext error, data 52e, v23f0,
            desc: Invalid credentials
        disabled user:
            info: 80090308: LdapErr: DSID-0C0903C5, comment: AcceptSecurityContext error, data 533, v23f0,
            desc: Invalid credentials
        password elapsed:
            info: 80090308: LdapErr: DSID-0C0903C5, comment: AcceptSecurityContext error, data 773, v23f0,
            desc: Invalid credentials
        wrong domain:
            info: 10000000, desc:
        """
        self.info = info
        self.desc = desc
        self.code = code
        
        if info.find(u'52e, v23f0') > 0:
            # wrong password, wrong user
            self.code = 1
            self.desc = u'Invalid credentials'
        elif info.find(u'533, v23f0') > 0:
            # disabled user
            self.code = 2
            self.desc = u'User is disabled'
        elif info.find(u'773, v23f0') > 0:
            # password elapsed
            self.code = 3
            self.desc = u'Password is expired'
        else:
            self.code = code
    
    def __str__(self):
        return u'code: %s, info: %s, desc: %s' % (self.code, self.info, self.desc)


class AbstractAuth(object):
    """Abstract auhtentication provider.
    
    :param user_class: User class returned if authentication succesfully. Class can be :class:`SystemUser` or a class
        that extend this one.
    """
    def __init__(self, user_class):
        self.logger = logging.getLogger(self.__class__.__module__ + u'.' + self.__class__.__name__)
        
        self.user_class = user_class

    def login(self, username, password, *args, **kvargs):
        """Base login method

        :param username: user name
        :param password: user password
        :return: System user
        :rtype: :class:`SystemUser`
        :raises AuthError: raise :class:`AuthError`          
        """
        raise NotImplementedError()

    def check(self, user_uuid, username):
        """Check user

        :param user_uuid: user uuid
        :param username: user name
        :return: System user
        :rtype: :class:`SystemUser`
        :raises AuthError: raise :class:`AuthError`
        """
        self.logger.debug(u'Check user: %s' % username)

        # create final user object
        user = self.user_class(user_uuid, username, None, True)

        self.logger.debug(u'Login succesfully: %s' % user)

        return user

    def refresh(self, username, uid):
        """Refresh login
        
        :param username: user name
        :param uid: login uid
        :return: System user
        :rtype: :class:`SystemUser`
        :raises AuthError: raise :class:`AuthError`        
        """
        # create final user object
        user = self.user_class(uid, username, None, True)
        self.logger.debug(u'Refresh %s successfully' % user)
        return user
