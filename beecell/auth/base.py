'''
Created on Jan 25, 2014

@author: darkbk
'''
import logging
from flask_login import UserMixin
from beecell.perf import watch

class SystemUser(UserMixin):
    """System user returned after authentication. Use this with flask_login. 
    """    
    confirmed_at = None
    last_login_at = None
    current_login_at = None
    last_login_ip = None
    current_login_ip = None
    login_count = None
    
    def __init__(self, uid, email, password, active, login_ip=None):
        self.logger = logging.getLogger(self.__class__.__module__+ \
                                        '.'+self.__class__.__name__)
        
        self.id = uid
        self.email = email
        self.password = password
        self.active = active
        self._roles = None
        self._perms = None
        self._attrib = None
        self.current_login_ip = login_ip
        
        self.logger.debug('Create flask_login user instance: %s, %s' % 
                          (uid, email))

    def __str__(self):
        return "<SystemUser id:'%s', name:'%s', active:'%s' ip='%s', roles='%s' attribs='%s'>" % (
               str(self.id), self.email, self.active, self.current_login_ip,
               self._roles, self._attrib)
    
    @watch
    def get_dict(self):
        return {u'id':self.id,
                u'name':self.email,
                u'attribute':self._attrib,
                u'active':self.active,
                u'roles':self._roles,
                u'perms':self._perms}

    @watch
    def set_groups(self, groups):
        self._groups = groups        
    
    @watch
    def get_groups(self):
        return self._groups          
    
    @watch
    def set_attributes(self, attrib):
        self._attrib = attrib  
    
    @watch
    def get_attributes(self):
        return self._attrib
    
    @watch
    def set_roles(self, roles):
        self._roles = roles

    @watch
    def get_roles(self):
        return self._roles

    @watch
    def set_perms(self, perms):
        self._perms = perms

    @watch
    def get_perms(self):
        return self._perms
    
    @watch
    def set_profile(self, profile):
        self._profile = profile

    @watch
    def get_profile(self):
        return self._profile

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
                info: 80090308: LdapErr: DSID-0C0903C5, comment: AcceptSecurityContext error, data 52e, v23f0, desc: Invalid credentials
            disabled user:
                info: 80090308: LdapErr: DSID-0C0903C5, comment: AcceptSecurityContext error, data 533, v23f0, desc: Invalid credentials
            password elapsed:
                info: 80090308: LdapErr: DSID-0C0903C5, comment: AcceptSecurityContext error, data 773, v23f0, desc: Invalid credentials
            wrong domain:
                info: 10000000, desc:
        """
        self.info = info
        self.desc = desc
        self.code = code
        
        if info.find('52e, v23f0') > 0:
            # wrong password, wrong user
            self.code = 1
            self.desc = "Invalid credentials"
        elif info.find('533, v23f0') > 0:
            # disabled user
            self.code = 2
            self.desc = "User is disabled"
        elif info.find('773, v23f0') > 0:
            # password elapsed
            self.code = 3
            self.desc = "Password is expired"
        else:
            self.code = code
    
    def __str__(self):
        return "code: %s, info: %s, desc: %s" % (self.code, self.info, self.desc)
    
class AbstractAuth(object):
    """Abstract auhtentication provider.
    
    :param user_class: User class returned if authentication succesfully.
                       Class can be :class:`SystemUser` or a class that 
                       extend this one.      
    """
    
    def __init__(self, user_class):
        self.logger = logging.getLogger(self.__class__.__module__+ \
                                        '.'+self.__class__.__name__)        
        
        self.user_class = user_class

    def login(self, username, password):
        """
        :param username: user name
        :param password: user password
        :return: System user
        :rtype: :class:`SystemUser`
        :raises AuthError: raise :class:`AuthError`          
        """
        raise NotImplementedError()
    
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
        self.logger.debug(u'Refresh %s successfully' % (user))        
        return user        