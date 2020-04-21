# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte


class ModelError(Exception):
    def __init__(self, value, code=404, *arg, **kw):
        """
        """
        self.value = str(value)
        self.code = code
        super(Exception, self).__init__(self.value, *arg, **kw)
        
    def __repr__(self):
        return "ModelError: %s" % self.value

    def __str__(self):
        return self.value


class TransactionError(Exception):
    def __init__(self, value, code=0, *arg, **kw):
        """
        """
        self.value = str(value)
        self.code = code
        super(Exception, self).__init__(self.value, *arg, **kw)
        
    def __repr__(self):
        return "TransactionError: %s" % self.value

    def __str__(self):
        return '%s' % self.value


class QueryError(Exception):
    def __init__(self, value, code=0, *arg, **kw):
        """
        """
        self.value = str(value)
        self.code = code
        super(Exception, self).__init__(self.value, *arg, **kw)
        
    def __repr__(self):
        return "QueryError: %s" % self.value

    def __str__(self):
        return self.value


from .manager import MysqlManager
