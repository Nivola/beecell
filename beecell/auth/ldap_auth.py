# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

from six import ensure_str
import ldap
from beecell.simple import truncate
from .base import AuthError, AbstractAuth


class LdapAuth(AbstractAuth):
    def __init__(
        self,
        host,
        user_class,
        port=None,
        timeout=30,
        ssl=False,
        dn="DC=users",
        search_filter=None,
        search_id="uid",
        bind_user=None,
        bind_pwd=None,
    ):
        """Ldap auhtentication provider

        :param host: Ldap hostname
        :param port: Ldap port number. Default=389 - ldap, 636 - ldaps
        :param user_class: extension of class base.SystemUser
        :param bool ssl: if True enable ldaps protocol
        :param int timeout: Set request time out
        :param str dn: set distinguished name [optional]
        :param search_filter: user search filter [optional]
        :param search_id: user search id [default=uid]
        :param bind_user: bind user name
        :param bind_pwd: bind user password
        """
        super(LdapAuth, self).__init__(user_class)

        self.host = host
        self.port = port
        self.dn = dn
        self.conn = None
        self.ssl = ssl
        self.timeout = timeout
        self.search_filter = search_filter
        self.search_id = search_id
        self.bind_user = bind_user
        self.bind_pwd = bind_pwd

    def __str__(self):
        return "<LdapAuth host:%s, port:%s, ssl:%s, dn:%s>" % (
            self.host,
            self.port,
            self.ssl,
            self.dn,
        )

    def connect(self):
        """Open connection to Ldap."""
        if self.ssl:
            self._connect_ssl()
        else:
            self._connect()

        self.conn.timeout = self.timeout
        self.conn.network_timeout = self.timeout
        return self.conn

    def _connect(self):
        """Open connection to Ldap."""
        if self.port is None:
            self.port = 389

        conn_uri = "ldap://%s:%s" % (self.host, self.port)
        self.conn = ldap.initialize(conn_uri)
        self.logger.debug("Open non-secure connection to %s" % conn_uri)

    def _connect_ssl(self):
        """Open connection to ldaps portal2."""
        if self.port is None:
            self.port = 636

        conn_uri = "ldaps://%s:%s" % (self.host, self.port)
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        self.conn = ldap.initialize(conn_uri)
        self.conn.set_option(ldap.OPT_REFERRALS, 0)
        self.conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        self.conn.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
        self.conn.set_option(ldap.OPT_X_TLS_DEMAND, True)
        self.logger.debug("Open secure connection to %s" % conn_uri)

    def close(self):
        """Close connection to Ldap."""
        if self.conn:
            self.conn.unbind_s()
            self.logger.debug("Close connection to %s" % self.conn)
            self.conn = None

    def query(self, query, fields=None):
        """Make a query on the Ldap.

        :param query: query string. Ex. ['sn']>>>
        :param fields: query fields
        :return: query response
        """
        if self.conn:
            try:
                # make query
                records = self.conn.search_s(self.dn, ldap.SCOPE_SUBTREE, query, fields)
                self.logger.debug("Query Ldap: %s" % query)
            except ldap.LDAPError as ex:
                self.logger.error("Ldap error: %s" % ex)

                try:
                    if "info" in ex[0]:
                        raise AuthError(ex[0]["info"], ex[0]["desc"])
                    else:
                        raise AuthError("", ex[0]["desc"], code=9)
                except:
                    raise AuthError("", ex, code=9)

            return records
        else:
            raise AuthError("", "No connection to server", code=0)

    def login1(self, username, password):
        """Login a user

        :param username: user name
        :param password: user password
        :return: instance of user_class
        """
        username = username.split("@")[0]
        self.logger.debug("Login user: %s" % (username))

        # open connect if it doesn't already exist
        if not self.conn:
            self.connect()

        try:
            domain_user = "%s@%s" % (username, self.domain)
            self.conn.simple_bind_s(domain_user, password.encode("utf8"))
        except (ldap.TIMEOUT, ldap.TIMELIMIT_EXCEEDED):
            raise AuthError("", "Connection error. Timeout limit was exceeded", code=7)
        except ldap.LDAPError as ex:
            self.logger.error("Ldap error: %s" % ex)
            self.close()
            self.conn = None

            if "info" in ex[0]:
                raise AuthError(ex[0]["info"], ex[0]["desc"])
            else:
                raise AuthError("", "Connection error: %s" % ex[0]["desc"], code=7)

        query = "sAMAccountName=%s" % username
        res = self.query(query)[0][1]
        self.close()

        attrib = {}
        groups = []
        for k, v in res.items():
            if k == "memberOf":
                # memberOf ['CN=reader,DC=clskdom,DC=lab', 'CN=admin,DC=clskdom,DC=lab']
                groups = [i.lstrip("CN=").split(",")[0] for i in v]
            elif k in [
                "primaryGroupID",
                "logonCount",
                "instanceType",
                "sAMAccountType",
                "uSNCreated",
                "badPwdCount",
                "codePage",
                "userAccountControl",
                "uSNChanged",
            ]:
                attrib[k] = int(v[0])
            elif k in [
                "lastLogonTimestamp",
                "badPasswordTime",
                "pwdLastSet",
                "accountExpires",
                "lastLogon",
            ]:
                attrib[k] = int(v[0])
            else:
                attrib[k] = v[0]

        uid = res["objectGUID"][0].encode("hex")
        user = self.user_class(uid, domain_user, password, True)
        user.set_attributes(attrib)
        user.set_groups(groups)

        self.logger.debug("Login succesfully: %s" % user)

        return user

    def authenticate(self, username, password, max_retry=3, cur_retry=0):
        """Authenticate a user

        :param username: user name
        :param password: user password
        :return: True
        """
        self.logger.debug("Authenticate user: %s" % username)

        # open connect if it doesn't already exist
        if self.conn is None:
            self.connect()

        try:
            self.conn.simple_bind_s(username, ensure_str(password))
        except (ldap.TIMEOUT, ldap.TIMELIMIT_EXCEEDED):
            self.logger.error("Ldap connection timeout")
            self.close()
            self.conn = None
            raise AuthError("", "Connection error. Timeout limit was exceeded", code=7)
        except ldap.CONNECT_ERROR:
            self.logger.error("Ldap connection error")
            self.close()
            self.conn = None
            raise AuthError("", "Connection error", code=7)
        except ldap.LDAPError as ex:
            self.logger.error("Ldap authentication error: %s" % ex)
            self.close()
            self.conn = None

            # {'desc': "Can't contact LDAP server", 'errno': 104, 'info': 'Connection reset by peer'}
            if str(ex).find("104") > 0:
                # check retry
                if cur_retry < max_retry:
                    cur_retry += 1
                    res = self.authenticate(username, password, max_retry=max_retry, cur_retry=cur_retry)
                    return res
                else:
                    raise AuthError("", "Ldap authentication error: %s" % ex, code=7)
            else:
                raise AuthError("", "Ldap authentication error: %s" % ex, code=7)
        return True

    def search_user(self, username, search_filter):
        """Search a user

        :param username: user name
        :param base_filter: filter used to search user
        :return: instance of user_class
        """
        query = search_filter.format(**username)
        res = self.query(query)

        if len(res) == 0 or res[0][0] is None:
            raise AuthError(
                "",
                "Ldap error - User %s was not found" % username.get("username"),
                code=5,
            )
        user = list(res[0])

        self.logger.debug("Get user record: %s" % truncate(user))

        return user

    def search_users(self, search_filter, fields=["cn", "mail"]):
        """Search users

        :param search_filter: filter used to search users
        :param fields: fields to search
        :return: instance of user_class
        """
        resp = []
        res = self.query(search_filter, fields=fields)
        for item in res:
            item = item[1]
            user = {}
            for field in fields:
                try:
                    value = item.get(field, None)
                    if len(value) == 1:
                        value = value[0]
                except:
                    value = ""
                user[ensure_str(field)] = ensure_str(value)
            resp.append(user)

        self.logger.debug("Get users: %s" % truncate(res))

        return resp

    def verify_user(self, username, password):
        """Search a user

        :param username: user name
        :param password: user password
        :return: instance of user_class
        """
        user = username
        user_attribs = {}
        if self.search_filter is not None:
            domain_user = {"username": username}
            # domain_user = username
            res = self.search_user(domain_user, self.search_filter)
            user = res[0]
            user_attribs = res[1]
            self.close()

        self.authenticate(user, password)

        attrib = {}
        groups = []
        for k, v in user_attribs.items():
            groups = []
            if k == "memberOf":
                groups.extend([ensure_str(i).lstrip("CN=").split(",")[0] for i in v])
            elif k == "objectClass":
                groups.extend([i for i in v])
            elif k in [
                "primaryGroupID",
                "logonCount",
                "instanceType",
                "sAMAccountType",
                "uSNCreated",
                "badPwdCount",
                "codePage",
                "userAccountControl",
                "uSNChanged",
            ]:
                attrib[k] = int(v[0])
            elif k in [
                "lastLogonTimestamp",
                "badPasswordTime",
                "pwdLastSet",
                "accountExpires",
                "lastLogon",
            ]:
                attrib[k] = int(v[0])
            else:
                attrib[k] = v[0]

        uid = ensure_str(user_attribs[self.search_id][0])
        user = self.user_class(uid, username, None, True)
        user.set_attributes(attrib)
        user.set_groups(groups)

        self.logger.debug("Login succesfully: %s" % user)

        return user

    def login(self, username, password):
        """Login a user

        :param username: user name
        :param password: user password
        :return: instance of user_class
        """
        self.authenticate(self.bind_user, self.bind_pwd)
        user = self.verify_user(username, password)

        return user
