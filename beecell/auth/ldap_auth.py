# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

import ldap
import platform
from .base import AuthError, AbstractAuth
from beecell.perf import watch


class LdapAuth(AbstractAuth):
    def __init__(self, host, domain, user_class, port=None, timeout=20, ssl=False, dn=None):
        """Ldap auhtentication provider
        
        :param host: Ldap hostname
        :param port: Ldap port number. Default=389 - ldap, 636 - ldaps
        :param domain: List of authentication domains. Es. ['clskdom.lab']
        :param profile_key: string like 'sAMAccountName'. Default='sAMAccountName'
        :param timeout: (int) Set request time out
        :param dn str: set distinguished name [optional]
        """
        super(LdapAuth, self).__init__(user_class)
        
        self.host = host
        self.port = port
        self.dn = None
        self.domain = domain
        self.conn = None
        self.ssl = ssl
        self.timeout = timeout
        
        # create dn string like 'DC=clskdom,DC=lab'
        domain_item = self.domain.split('.')
        # create dn based on platform
        dist = platform.dist()
        if dn is not None:
            self.dn = dn
        else:
            if dist[0] == 'centos':
                self.dn = "DC="+",DC=".join(domain_item)
            elif dist[0] == 'fedora':
                self.dn = "ou=user,DC="+",DC=".join(domain_item)
            else:
                self.dn = "DC="+",DC=".join(domain_item)

    def __str__(self):
        return "<LdapAuth host:%s, port:%s, ssl:%s, dn:%s>" % (
               self.host, self.port, self.ssl, self.dn)

    @watch
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
        if self.port == None:
            self.port = 389
            
        conn_uri = 'ldap://%s:%s' % (self.host, self.port)
        self.conn = ldap.initialize(conn_uri)
        self.logger.debug('Open non-secure connection to %s' % conn_uri)

    def _connect_ssl(self):
        """Open connection to ldaps portal2."""
        if self.port == None:
            self.port = 636
            
        conn_uri = 'ldaps://%s:%s' % (self.host, self.port)    
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        self.conn = ldap.initialize(conn_uri)
        self.conn.set_option(ldap.OPT_REFERRALS, 0)
        self.conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        self.conn.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
        self.conn.set_option( ldap.OPT_X_TLS_DEMAND, True)
        self.logger.debug('Open secure connection to %s' % conn_uri)

    @watch
    def close(self):
        """Close connection to Ldap."""
        if self.conn:
            self.conn.unbind_s()
            self.logger.debug('Close connection to %s' % self.conn)
            self.conn = None

    def _query(self, query):
        """Make a query on the Ldap.
        
        Return: query response
        """
        if self.conn:
            try:
                # make query
                print query
                print self.dn
                records = self.conn.search_s(self.dn, ldap.SCOPE_SUBTREE, query)
                self.logger.debug('Query Ldap: %s' % query)
            except ldap.LDAPError as ex:
                #self.close()
                #self.conn = None
                self.logger.error("Ldap error: %s" % ex)
                
                try:
                    if 'info' in ex[0]:
                        raise AuthError(ex[0]['info'], ex[0]['desc'])
                    else:
                        raise AuthError('', ex[0]['desc'], code=9)
                except:
                    raise AuthError('', ex, code=9)
                
            return records
        else:
            raise AuthError('', 'No connection to server', code=0)

    @watch
    def login(self, username, password):
        """Login a user

        :param username: user name
        :param password: user password
        :return: instance of user_class
        """
        username = username.split('@')[0]
        self.logger.debug('Login user: %s' % (username))
        
        # open connect if it doesn't already exist
        if not self.conn:
            self.connect()

        try:
            domain_user = "%s@%s" % (username, self.domain)
            self.conn.simple_bind_s(domain_user, password.encode('utf8'))
        except (ldap.TIMEOUT, ldap.TIMELIMIT_EXCEEDED):
            raise AuthError("", "Connection error. Timeout limit was exceeded", code=7)            
        except ldap.LDAPError as ex:
            self.logger.error("Ldap error: %s" % ex)
            self.close()
            self.conn = None

            if 'info' in ex[0]:
                raise AuthError(ex[0]['info'], ex[0]['desc'])
            else:
                raise AuthError("", "Connection error: %s" % ex[0]['desc'], code=7)

        query = "sAMAccountName=%s" % username
        res = self._query(query)[0][1]
        self.close()
        
        attrib = {}
        groups = []
        for k, v in res.iteritems():
            if k == 'memberOf':
                # memberOf ['CN=reader,DC=clskdom,DC=lab', 'CN=admin,DC=clskdom,DC=lab']
                groups = [i.lstrip('CN=').split(',')[0] for i in v]
            elif k in ['primaryGroupID', 'logonCount', 'instanceType', 'sAMAccountType', 'uSNCreated', 'badPwdCount',
                       'codePage', 'userAccountControl', 'uSNChanged']:
                attrib[k] = int(v[0])
            elif k in ['lastLogonTimestamp', 'badPasswordTime', 'pwdLastSet', 'accountExpires', 'lastLogon']:
                attrib[k] = int(v[0])                
            else:
                attrib[k] = v[0]
        
        uid = res['objectGUID'][0].encode("hex")
        user = self.user_class(uid, domain_user, password, True)
        user.set_attributes(attrib)
        user.set_groups(groups)

        self.logger.debug('Login succesfully: %s' % user)

        return user
