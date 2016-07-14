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
        return "TransactionError: %s" % self.desc
    
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
        return "QueryError: %s" % self.desc

from .manager import MysqlManager