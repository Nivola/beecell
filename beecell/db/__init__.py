class ModelError(Exception):
    def __init__(self, desc, code=0):
        """
        """
        self.desc = desc
        self.code = code
        Exception.__init__(self, desc)
        
    def __repr__(self):
        return "ModelError: %s" % self.desc

    def __str__(self):
        return u'%s, %s' % (self.desc, self.code)

class ModelError(Exception):
    def __init__(self, desc, code=404):
        """
        """
        self.desc = desc
        self.code = code
        Exception.__init__(self, desc)
        
    def __repr__(self):
        return "ModelError: %s" % self.desc

    def __str__(self):
        return self.desc

class TransactionError(Exception):
    def __init__(self, desc, code=0):
        """
        """
        self.desc = desc
        self.code = code
        Exception.__init__(self, desc)
        
    def __repr__(self):
        return "TransactionError: %s" % self.desc

    def __str__(self):
        return u'%s, %s' % (self.desc, self.code)
    
class QueryError(Exception):
    def __init__(self, desc, code=0):
        """
        """
        self.desc = desc
        self.code = code
        Exception.__init__(self, desc)
        
    def __repr__(self):
        return "QueryError: %s" % self.desc

    def __str__(self):
        return u'%s, %s' % (self.desc, self.code)

from .manager import MysqlManager