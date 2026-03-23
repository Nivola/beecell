# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte

from __future__ import annotations
from time import sleep
from typing import Dict, List, Optional, TYPE_CHECKING
from bonsai import (
    LDAPClient,
    LDAPConnection,
    LDAPSearchScope,
    LDAPError,
    TimeoutError as LdapTimeoutError,
    ConnectionError as LdapConnectionError,
    AuthenticationError
)
from beecell.simple import truncate
from beecell.auth.base import AuthError, AbstractAuth
from beecell.auth.ldap_conversion_utils import ldap_entry_to_dict
if TYPE_CHECKING:
    from bonsai import LDAPEntry
    from beecell.auth.base import SystemUser

class LdapAuth(AbstractAuth):
    def __init__(
        self,
        host: str,
        user_class: SystemUser,
        port: Optional[int]=None,
        timeout=30,
        ssl=True,
        dn="DC=users",
        search_filter: Optional[str]=None,
        search_id="uid",
        bind_user: Optional[str]=None,
        bind_pwd: Optional[str]=None,
        max_retries = 2
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
        super().__init__(user_class)

        self.host = host
        self.port = port or (636 if ssl else 389)
        self.dn = dn
        self.ssl = ssl
        self.timeout = timeout
        self.search_filter = search_filter
        self.search_id = search_id
        self.bind_user = bind_user
        self.bind_pwd = bind_pwd

        self._client: Optional[LDAPClient] = None
        self._conn: Optional[LDAPConnection] = None

        self.max_retries = max_retries

    def __str__(self):
        return "<LdapAuth host:%s, port:%s, ssl:%s, dn:%s>" % (
            self.host,
            self.port,
            self.ssl,
            self.dn,
        )

    @property
    def conn(self):
        """property to handle a lazy reusable connection"""
        if self._conn and not self._conn.closed:
            return self._conn
        self.connect()
        return self._conn

    def close(self, abandon_requests=True):
        """Close connection to Ldap."""
        if self._conn and not self._conn.closed:
            self.logger.debug("Closing ldap connection to %s", self._conn)
            self._conn.close(abandon_requests=abandon_requests)
        self._conn = None

    def __enter__(self):
        """enter and exit for context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """enter and exit for context manager support"""
        self.close()

    def set_admin_credentials(self):
        """set admin credentials"""
        if self._client and self.bind_user:
            if (
                self._client.credentials is None or
                self._client.credentials.get("user")!=self.bind_user
            ):
                self.close()
                self._client.set_credentials("SIMPLE", user=self.bind_user, password=self.bind_pwd)

    def set_user_credentials(self, username, password):
        """set specified user credentials"""
        if self._client and (
            self._client.credentials is None or
            self._client.credentials.get("user")!=username
        ):
            self.close()
            self._client.set_credentials("SIMPLE", user=username, password=password)

    def connect(self):
        """Open connection to Ldap."""
        conn_uri = ""
        if self.ssl:
            # ldaps
            conn_uri = f"ldaps://{self.host}:{self.port}"
            self.logger.debug("Opening secure connection to %s", conn_uri)
        else:
            conn_uri = f"ldap://{self.host}:{self.port}"
            self.logger.debug("Opening non-secure connection to %s", conn_uri)

        if self._client is None:
            self._client = LDAPClient(conn_uri)
            if self.ssl:
                self._client.set_cert_policy("never")

            self._client.set_server_chase_referrals(False)

            # only set here once, then reset as needed
            if self.bind_user:
                self.set_admin_credentials()

        for attempt in range(self.max_retries+1):
            try:
                self._conn = self._client.connect(timeout=self.timeout)
                self.conn.whoami() # make sure credentials are correct with a dummy call
                return
            except (LdapConnectionError, LdapTimeoutError) as ex:
                self.logger.warning("Ldap connection error: %s", ex)
                if attempt==self.max_retries:
                    self.close()
                    raise AuthError("", "Ldap connection error", 7) from ex
                sleep(5)
            except (AuthenticationError, LDAPError) as ex:
                self.close()
                self.logger.error("Ldap authentication error %s", ex)
                raise AuthError("", "Ldap authentication error", 9) from ex

        raise AuthError("","unexpected error", 9)

    def ldap_entry_user_repr(self, user_entry: Optional['LDAPEntry'], username: str):
        """convert ldap entry to user representation, or return empty user object"""
        attrib = {}
        groups = []
        user_dict = {}
        if user_entry:
            user_dict = ldap_entry_to_dict(user_entry)
            for k, v in user_dict.items():
                if k == "memberOf":
                    # safely extract CN from each DN
                    for dn in v if isinstance(v, list) else [v]:
                        if isinstance(dn, str) and dn.upper().startswith("CN="):
                            # memberOf ['CN=reader,DC=clskdom,DC=lab', 'CN=admin,DC=clskdom,DC=lab']
                            groups.append(dn[3:].split(",")[0])
                elif k == "objectClass":
                    groups.extend(v if isinstance(v, list) else [v])
                elif k in [
                    "primaryGroupID", "logonCount", "instanceType", "sAMAccountType",
                    "uSNCreated", "badPwdCount", "codePage", "userAccountControl", "uSNChanged",
                    "lastLogonTimestamp", "badPasswordTime", "pwdLastSet",
                    "accountExpires", "lastLogon",
                ]:
                    # safely convert to int if possible
                    try:
                        attrib[k] = int(v) if not isinstance(v, list) else int(v[0])
                    except Exception:
                        attrib[k] = v
                else:
                    attrib[k] = v

        #uid = user_dict.get("objectGUID")
        uid = user_dict.get(self.search_id)
        user: 'SystemUser' = self.user_class(uid, username, None, active=True)
        user.set_attributes(attrib)
        user.set_groups(groups)
        return user


    def query(self, query, fields: Optional[List[str]]=None):
        """Make a query on the Ldap.

        :param query: query string. Ex. ['sn']>>>
        :param fields: query fields. NB:
        - fields=None -> return all attributes
        - fields=[]   -> return no attributes
        :return: query response
        """
        try:
            records = self.conn.search(
                self.dn, LDAPSearchScope.SUBTREE,
                filter_exp=query, attrlist=fields
            )
            self.logger.debug("Query Ldap: %s", query)
        except (LdapConnectionError, LdapTimeoutError) as ex:
            self.logger.error("Ldap connection error %s", ex)
            self.close()
            raise AuthError("", "Ldap connection error", 7) from ex
        except LDAPError as ex:
            self.close()
            self.logger.error("Ldap error: %s", ex)
            raise AuthError("", "Ldap error", 9) from ex

        return records

    def search_user(
        self, search_filter: str, search_params: Dict[str, str],
        check_existence_only = False, convert_to_dict = False
    ):
        """Search a user

        :param username: user name
        :param base_filter: filter used to search user
        :return: LDAPentry representing user, or if convert_to_dict, dict representation
        """
        query = search_filter.format(**search_params)
        fields = None # i.e. all attributes
        if check_existence_only:
            fields = ["dn"]
        res = self.query(query, fields=fields)

        username = search_params.get("username")

        if not res or len(res) == 0 or res[0] is None:
            raise AuthError("", f"Ldap error - User {username} was not found", code=5)

        self.logger.debug2("Found %d records for user %s", len(res), username)

        user_entry = res[0]

        self.logger.debug("Get user record: %s", truncate(user_entry))

        if convert_to_dict and user_entry:
            user_entry = ldap_entry_to_dict(user_entry)

        return user_entry

    def search_users(self, search_filter, fields=["cn", "mail"]):
        """Search users

        :param search_filter: filter used to search users
        :param fields: fields to search
        :return: instance of user_class
        """
        resp = []
        res = self.query(search_filter, fields=fields)
        for item in res:
            resp.append(ldap_entry_to_dict(item, fields=fields))

        self.logger.debug("Get users: %s", truncate(res))

        return resp

    def verify_user(
        self, username: Optional[str] = None, password: Optional[str] = None,
        user: Optional[SystemUser] = None
    ):
        """Search a user

        :param username: user name
        :param password: user password
        :return: instance of user_class
        """
        if username is None and user is None:
            raise AuthError("", "Provide one of 'user' or 'username'", 9)

        if user:
            # name = email
            username: Optional[str] = user.get_dict().get("name")

        if self.search_filter is not None:
            domain_user = {"username": username}
            self.set_admin_credentials()
            search_result: 'LDAPEntry' = self.search_user(
                search_params=domain_user,
                search_filter=self.search_filter,
                convert_to_dict=False
            )
        else:
            raise AuthError("", "search_filter missing", 9)

        self.set_user_credentials(username, password)
        try:
            _auth_identity_string = self.conn.whoami()
            # e.g. 'u:DOMNT\\12345'
        except Exception as ex:
            # if anonymous bind is disabled
            # and user credentials are wrong
            # during self.conn we'll get an AuthError
            self.logger.error("user verification failed: %s", ex)
            raise AuthError("", f"user verification failed: {ex}", 9) from ex
        finally:
            self.set_admin_credentials()

        found_user = self.ldap_entry_user_repr(search_result, username=username)

        self.logger.debug("Login succesfully: %s", found_user)
        return found_user

    def login(self, username, password, *args, **kvargs):
        """Login a user

        :param username: user name
        :param password: user password
        :return: instance of user_class
        """
        user = self.verify_user(username, password)

        return user
