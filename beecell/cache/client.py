# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte

import logging
import ujson as json

from beecell.simple import truncate


class CacheClient(object):
    """ """
    def __init__(self, redis, prefix=u'cache.'):
        """Initialize cache client

        :param redis: redis manager reference (redis.StrictRedis or StrictRedisCluster instance)
        :param prefix: chache key prefix
        """
        self.logger = logging.getLogger(self.__class__.__module__ + u'.' + self.__class__.__name__)

        self.redis = redis
        self.prefix = prefix

    def set(self, key, value, ttl=600):
        """Set a cache item

        :param key: cache item key
        :param value: cache item value
        :param ttl: item time to live [default=600s]
        :return: True
        """
        value = json.dumps({u'data': value})
        self.redis.setex(self.prefix + key, ttl, value)
        self.logger.debug(u'Set cache item %s:%s [%ss]' % (key, truncate(value), ttl))
        return True

    def get(self, key):
        """Get a cache item

        :param key: cache item key
        :return: value
        """
        value = self.redis.get(self.prefix + key)
        if value is not None:
            value = json.loads(value).get(u'data')
        self.logger.debug(u'Get cache item %s:%s' % (key, truncate(value)))
        return value

    def expire(self, key, ttl=600):
        """Set key expire time

        :param key: cache item key
        :param ttl: item time to live [default=600s]
        :return: True
        """
        value = self.redis.expire(self.prefix + key, ttl)
        self.logger.debug(u'Set cache item %s expire to %s' % (key, ttl))
        return True

    def delete(self, key):
        """Delete a cache item

        :param key: cache item key
        :return: True
        """
        value = self.redis.delete(self.prefix + key)
        self.logger.debug(u'Delete cache item %s' % key)
        return True

    def extend_ttl(self, key, ttl=600):
        """Extend a cache item ttl

        :param key: cache item key
        :return: True
        """
        value = self.redis.expire(self.prefix + key, ttl)
        self.logger.debug(u'Extend cache item %s ttl to %s' % (key, ttl))
        return True
