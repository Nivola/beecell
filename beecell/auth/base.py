# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

import logging
from flask_login import UserMixin
from typing import List, Union


class SystemUser(UserMixin):
    """System user returned after authentication. Use this with flask_login."""

    confirmed_at = None
    last_login_at = None
    current_login_at = None
    last_login_ip = None
    current_login_ip = None
    login_count = None

    def __init__(self, uid, email, password, active, login_ip=None, domain=None):
        self.logger = logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)

        self.id: str = uid
        self.email: str = email
        self.password: str = password
        self.active = active
        self.domain: str = domain
        self._roles: List[str] = None
        self._perms = None
        self._attrib = None
        self.current_login_ip: str = login_ip

        self.logger.debug("Create flask_login user instance: %s, %s" % (uid, email))

    def __str__(self):
        return "<SystemUser id: %s, name: %s, active: %s ip= %s>" % (
            self.id,
            self.email,
            self.active,
            self.current_login_ip,
        )

    def get_dict(self):
        return {
            "id": self.id,
            "name": self.email,
            "domain": self.domain,
            "active": self.active,
            "roles": self._roles,
            "perms": self._perms,
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
    """Authentication provider exception."""

    INVALIDCREDENTIALS: int = 1
    USERDISABLED: int = 2
    PASSWORDEXPIRED: int = 3
    WRONGPASSWORD: int = 4
    USERNOTEXIST: int = 5
    CONNECTIONERROR: int = 7
    UNDEFINED: int = 9
    DOMAINERROR: int = 10
    TOKENEXPIRED: int = 11
    FORBIDDEN: int = 12

    def __init__(self, info: str = "", desc: str = "", code=None):
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

        if info.find("52e, v23f0") > 0:
            # wrong password, wrong user
            self.code = 1
            self.desc = "Invalid credentials"
        elif info.find("533, v23f0") > 0:
            # disabled user
            self.code = 2
            self.desc = "User is disabled"
        elif info.find("773, v23f0") > 0:
            # password elapsed
            self.code = 3
            self.desc = "Password is expired"
        else:
            self.code = code

    def __str__(self):
        return "code: %s, info: %s, desc: %s" % (self.code, self.info, self.desc)


class AbstractAuth(object):
    """Abstract auhtentication provider.

    :param user_class: User class returned if authentication succesfully. Class can be :class:`SystemUser` or a class
        that extend this one.
    """

    def __init__(self, user_class):
        self.logger = logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)

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
        self.logger.debug("Check user: %s" % username)

        # create final user object
        user = self.user_class(user_uuid, username, None, True)

        self.logger.debug("Login succesfully: %s" % user)

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
        self.logger.debug("Refresh %s successfully" % user)
        return user
