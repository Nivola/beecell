'''
Created on Nov 11, 2014

@author: darkbk
'''
from beecell.auth import LdapAuth

class SystemUser():
    confirmed_at = None
    last_login_at = None
    current_login_at = None
    last_login_ip = None
    current_login_ip = None
    login_count = None
    
    def __init__(self, uid, email, password, active):
        """System user returned after authentication. Use this with flask_login. """
        self.id = uid
        self.email = email
        self.password = password
        self.active = active
        self._roles = None
        self._perms = None
        self._profile = None

    def __str__(self):
        return "<SystemUser id: %s, name: %s, active: %s>" % (
               str(self.id), self.email, self.active)
    
    def get_dict(self):
        return {'id':self.id,
                'name':self.email,
                'active':self.active,
                'roles':self._roles,
                'perms':self._perms,
                'profile':self._profile}

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
    
    def set_profile(self, profile):
        self._profile = profile

    def get_profile(self):
        return self._profile

ldap_host = "ad.comune.torino.it"
ldap_port = 389
ldap_domain = "ad.comune.torino.it"
ldap_timeout = 100

auth_provider = LdapAuth(ldap_host, ldap_domain, 
                         SystemUser, port=ldap_port, 
                         timeout=ldap_timeout, ssl=False)
#self.user = "admin@clskdom.lab"
#self.password = "admin_01"
user = "_test@ad.comune.torino.it"
password = "Password0"

auth_provider.login(user, password)
