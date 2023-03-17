# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

from beecell.simple import jsonDumps

import logging
import ujson as json
from beecell.simple import truncate
import redis
import pickle
import codecs
from typing import Any


class CacheClient(object):
    """ """

    def __init__(self, redis: redis.StrictRedis, prefix="cache."):
        """Initialize cache client

        :param redis: redis manager reference (redis.StrictRedis or StrictRedisCluster instance)
        :param prefix: chache key prefix
        """
        self.logger = logging.getLogger(
            self.__class__.__module__ + "." + self.__class__.__name__
        )

        self.redis = redis
        self.prefix = prefix

    def ping(self):
        self.redis.ping()

    def set(self, key: str, value, ttl=600, pickling=False):
        """Set a cache item

        :param key: cache item key
        :param value: cache item value
        :param ttl: item time to live [default=600s]
        :param picling: if true marshal value using pickle otherways use json [default=False]
        :return: True
        """
        if pickling:
            pickled = codecs.encode(pickle.dumps(value), "base64").decode()
            cachevalue = jsonDumps({"pickled": pickled})
        else:
            cachevalue = jsonDumps({"data": value})
        self.redis.setex(self.prefix + key, ttl, cachevalue)
        self.logger.debug(
            "Set cache item %s:%s [%ss]" % (key, truncate(cachevalue), ttl)
        )
        return True

        ##unpickled = pickle.loads(codecs.decode(pickled.encode(), "base64"))
        self.redis.setex(self.prefix + key, ttl, cachevalue)
        self.logger.debug(
            "Set cache item %s:%s [%ss]" % (key, truncate(cachevalue), ttl)
        )
        return True

    def get(self, key: str) -> Any:
        """Get a cache item

        :param key: cache item key
        :return: value
        """
        value = self.redis.get(self.prefix + key)
        if value is not None:
            # if found the cached data foe key
            # get envelop we axpect data for json-marshaled or pickeled for pickled
            envelop: dict = json.loads(value)
            value = envelop.get("data", None)
            if value is None:
                pickled = envelop.get("pickled", None)
                if pickled is not None:
                    value = pickle.loads(codecs.decode(pickled.encode(), "base64"))
        self.logger.debug("Get cache item %s:%s" % (key, truncate(value)))
        return value

    def expire(self, key, ttl=600):
        """Set key expire time

        :param key: cache item key
        :param ttl: item time to live [default=600s]
        :return: True
        """
        value = self.redis.expire(self.prefix + key, ttl)
        self.logger.debug("Set cache item %s expire to %s" % (key, ttl))
        return True

    def delete(self, key):
        """Delete a cache item

        :param key: cache item key
        :return: True
        """
        value = self.redis.delete(self.prefix + key)
        self.logger.debug("Delete cache item %s" % key)
        return True

    def get_by_pattern(self, pattern):
        """Get keys by pattern

        :param pattern: key search pattern
        :return: list of items
        """
        keys = self.redis.keys(self.prefix + pattern)
        res = []
        for key in keys:
            res.append({"key": key, "value": self.redis.get(key)})
        return res

    def delete_by_pattern(self, pattern):
        """Delete keys by pattern

        :param pattern: key search pattern
        :return: True
        """
        keys = self.redis.keys(self.prefix + pattern)
        if len(keys) > 0:
            res = self.redis.delete(*keys)
            return res
        return True

    def extend_ttl(self, key, ttl=600):
        """Extend a cache item ttl

        :param key: cache item key
        :return: True
        """
        value = self.redis.expire(self.prefix + key, ttl)
        self.logger.debug("Extend cache item %s ttl to %s" % (key, ttl))
        return True
