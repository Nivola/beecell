'''
Created on Apr 26, 2014

@author: darkbk
'''
class AuthDbManagerError(Exception): pass
class AbstractAuthDbManager(object):
    """
    """   
    def __init__(self, session=None):
        """ """
        self._session = session

    def get_user(self, name=None):
        """Get user object from name.
        
        :param name: name of the user
        """
        return NotImplemented

    def verify_user_password(self, user, password):
        """Verify user password.
        
        :param user: Orm User istance
        :param password: Password to verify
        """
        return NotImplemented