# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

import sys
import logging
from celery.utils.log import ColorFormatter as CeleryColorFormatter
from celery.utils.term import colored

DEBUG2 = -10
DEBUG3 = -20


class ExtendedLogger(logging.Logger):
    def debug2(self, msg, *args, **kwargs):
        if DEBUG2 >= self.getEffectiveLevel():
            self._log(DEBUG2, msg, args, **kwargs)

    def debug3(self, msg, *args, **kwargs):
        if DEBUG3 >= self.getEffectiveLevel():
            self._log(DEBUG3, msg, args, **kwargs)


logging.setLoggerClass(ExtendedLogger)
logging.addLevelName(DEBUG2, u'DEBUG2')
logging.addLevelName(DEBUG3, u'DEBUG3')


class CustomFormatter(logging.Formatter):
    def __init__(self, default):
        self._default_formatter = default
        
    def format(self, record):
        return self._default_formatter.format(record)


class ColorFormatter(CeleryColorFormatter):
    """Logging formatter that adds colors based on severity."""

    #: Loglevel -> Color mapping.
    COLORS = colored().names
    colors = {
        u'DEBUG': COLORS[u'blue'], 
        u'WARNING': COLORS[u'yellow'],
        u'WARN': COLORS[u'yellow'],
        u'ERROR': COLORS[u'red'], 
        u'CRITICAL': COLORS[u'magenta'],
        u'DEBUG2': COLORS[u'green'],
        u'DEBUG3': COLORS[u'cyan']
    }  


class LoggerHelper(object):
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0
    DEBUG2 = DEBUG2
    DEBUG3 = DEBUG3

    #
    # new methods. Correct the problem with loggers that use the same file. Use 
    # rotatingfile_handler passing all the logger.
    #
    @staticmethod
    def memory_handler(loggers, logging_level, target, frmt=None, formatter=ColorFormatter):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s"

        handler = logging.handlers.MemoryHandler(capacity=1000, target=target)
        handler.setLevel(logging_level)
        if formatter is None:
            handler.setFormatter(logging.Formatter(frmt))
        else:
            handler.setFormatter(formatter(frmt))
            
        for logger in loggers:
            logger.addHandler(handler)
            logger.setLevel(logging_level)
            logger.propagate = False
    
    @staticmethod
    def simple_handler(loggers, logging_level, frmt=None, formatter=ColorFormatter):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s"

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging_level)
        if formatter is None:
            handler.setFormatter(logging.Formatter(frmt))
        else:
            handler.setFormatter(formatter(frmt))

        for logger in loggers:
            logger.addHandler(handler)
            logger.setLevel(logging_level)
            logger.propagate = False  
    
    @staticmethod
    def rotatingfile_handler(loggers, logging_level, file_name, maxBytes=104857600, backupCount=10, frmt=None,
                             formatter=ColorFormatter):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s"
        handler = logging.handlers.RotatingFileHandler(file_name, mode=u'a', maxBytes=maxBytes, backupCount=backupCount)
        handler.setLevel(logging_level)
        if formatter is None:
            handler.setFormatter(logging.Formatter(frmt))
        else:
            handler.setFormatter(formatter(frmt))
        
        for logger in loggers:
            logger.addHandler(handler)
            logger.setLevel(logging_level)
            logger.propagate = False
            
    @staticmethod
    def file_handler(loggers, logging_level, file_name, frmt=None, formatter=ColorFormatter):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s"
        handler = logging.FileHandler(file_name, mode=u'a')
        handler.setLevel(logging_level)
        if formatter is None:
            handler.setFormatter(logging.Formatter(frmt))
        else:
            handler.setFormatter(formatter(frmt))        
        
        for logger in loggers:
            logger.addHandler(handler)
            logger.setLevel(logging_level)
            logger.propagate = False
