# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte

import sys
import logging
from celery.utils.log import ColorFormatter as CeleryColorFormatter
from celery.utils.term import colored

from beecell.logger.elasticsearch import ElasticsearchHandler, ElasticsearchFormatter

DEBUG2 = -10
DEBUG3 = -20

module_logger = logging.getLogger(__name__)


class ExtendedLogger(logging.Logger):
    def debug2(self, msg, *args, **kwargs):
        if DEBUG2 >= self.getEffectiveLevel():
            self._log(DEBUG2, msg, args, **kwargs)

    def debug3(self, msg, *args, **kwargs):
        if DEBUG3 >= self.getEffectiveLevel():
            self._log(DEBUG3, msg, args, **kwargs)


logging.setLoggerClass(ExtendedLogger)
logging.addLevelName(DEBUG2, 'DEBUG2')
logging.addLevelName(DEBUG3, 'DEBUG3')


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
        'DEBUG': COLORS['blue'], 
        'WARNING': COLORS['yellow'],
        'WARN': COLORS['yellow'],
        'ERROR': COLORS['red'], 
        'CRITICAL': COLORS['magenta'],
        'DEBUG2': COLORS['green'],
        'DEBUG3': COLORS['cyan']
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
    def simple_handler(loggers, logging_level, frmt=None, formatter=ColorFormatter, propagate=False):
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
            logger.propagate = propagate
    
    @staticmethod
    def rotatingfile_handler(loggers, logging_level, file_name, maxBytes=104857600, backupCount=10, frmt=None,
                             formatter=ColorFormatter, propagate=False):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s"
        handler = logging.handlers.RotatingFileHandler(file_name, mode='a', maxBytes=maxBytes, backupCount=backupCount)
        handler.setLevel(logging_level)
        if formatter is None:
            handler.setFormatter(logging.Formatter(frmt))
        else:
            handler.setFormatter(formatter(frmt))
        
        for logger in loggers:
            logger.addHandler(handler)
            logger.setLevel(logging_level)
            logger.propagate = propagate
            
    @staticmethod
    def file_handler(loggers, logging_level, file_name, frmt=None, formatter=ColorFormatter, propagate=False):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s"
        handler = logging.FileHandler(file_name, mode='a')
        handler.setLevel(logging_level)
        if formatter is None:
            handler.setFormatter(logging.Formatter(frmt))
        else:
            handler.setFormatter(formatter(frmt))        
        
        for logger in loggers:
            logger.addHandler(handler)
            logger.setLevel(logging_level)
            logger.propagate = propagate

    @staticmethod
    def elastic_handler(loggers, logging_level, client, frmt=None, propagate=False, index='log', tags=[],
                        **custom_fields):
        """Configure a logging handler that use elasticsearch as backend.

        :param loggers: list of loggers
        :param logging_level: logging level
        :param client: elasticsearch.Elasticsearch class instance
        :param index: elasticsearch index name
        :param tags: list of tags to add [optional]
        :param frmt: log format [optional]
        :param custom_fields: custom fields as key=value
        """
        if frmt is None:
            frmt = '{"timestamp":"%(asctime)s","levelname":"%(levelname)s","process":"%(process)s",' \
                   '"thread":"%(thread)s","module":"%(name)s","func":"%(funcName)s","lineno":"%(lineno)d",' \
                   '"message":"%(message)s"}'
        handler = ElasticsearchHandler(client, index=index, tags=tags, **custom_fields)
        handler.setLevel(logging_level)
        handler.setFormatter(ElasticsearchFormatter(frmt))

        for logger in loggers:
            logger.addHandler(handler)
            logger.setLevel(logging_level)
            logger.propagate = propagate
