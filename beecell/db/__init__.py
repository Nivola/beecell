class TransactionError(Exception):
    def __init__(self, desc, code=0):
        """
        """
        self.desc = desc
        self.code = code
        
    def __str__(self):
        return "(TransactionError) (%s, %s)" % (self.code, self.desc)    
    
class QueryError(Exception):
    def __init__(self, desc, code=0):
        """
        """
        self.desc = desc
        self.code = code
        
    def __str__(self):
        return "(QueryError) (%s, %s)" % (self.code, self.desc)

from .manager import MysqlManager