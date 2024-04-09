# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

import logging
import ujson as json
import pickle
import codecs
from typing import Any
from beecell.db.manager import RedisManager
from beecell.simple import truncate, jsonDumps


class CacheClient(object):
    """ """

    def __init__(self, redis_manager: RedisManager, prefix="cache."):
        """Initialize cache client

        :param redis: redis manager reference (RedisManager)
        :param prefix: chache key prefix
        """
        self.logger = logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)

        self.redis_manager = redis_manager
        self.prefix = prefix

    def ping(self):
        self.redis_manager.ping()

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
        self.redis_manager.setex(self.prefix + key, ttl, cachevalue)
        self.logger.debug("Set cache item %s:%s [%ss]" % (key, truncate(cachevalue), ttl))
        return True

    def get(self, key: str) -> Any:
        """Get a cache item

        :param key: cache item key
        :return: value
        """
        value = self.redis_manager.get(self.prefix + key)
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

    def expire(self, key, ttl=600) -> bool:
        """Set key expire time

        :param key: cache item key
        :param ttl: item time to live [default=600s]
        :return: True
        """
        ret = self.redis_manager.expire(self.prefix + key, ttl)
        self.logger.debug("Set cache item %s expire to %s - ret: %s" % (key, ttl, ret))
        return ret

    def delete(self, key):
        """Delete a cache item

        :param key: cache item key
        :return: True
        """
        self.redis_manager.delete(self.prefix + key)
        self.logger.debug("Delete cache item %s" % key)
        return True

    def get_by_pattern(self, pattern):
        """Get keys by pattern

        :param pattern: key search pattern
        :return: list of items
        """
        # print("+++++ CacheClient - get_by_pattern - pattern: %s" % pattern)
        keys = self.redis_manager.keys(self.prefix + pattern)
        # print("+++++ CacheClient - get_by_pattern - keys: %s" % keys)
        res = []
        if keys is not None:
            for key in keys:
                res.append({"key": key, "value": self.redis_manager.get(key)})
        return res
    
    def get_keys_by_pattern(self, pattern):
        """Get keys by pattern

        :param pattern: key search pattern
        :return: list of items
        """
        # print("+++++ CacheClient - get_by_pattern - pattern: %s" % pattern)
        keys = self.redis_manager.keys(self.prefix + pattern)
        # print("+++++ CacheClient - get_by_pattern - keys: %s" % keys)
        return keys

    def delete_by_pattern(self, pattern):
        """Delete keys by pattern

        :param pattern: key search pattern
        :return: True
        """
        # print("+++++ CacheClient - delete_by_pattern - pattern: %s" % pattern)
        res = self.redis_manager.delete(self.prefix + pattern)
        return res

    def extend_ttl(self, key, ttl=600) -> bool:
        """Extend a cache item ttl

        :param key: cache item key
        :return: True
        """
        ret = self.redis_manager.expire(self.prefix + key, ttl)
        self.logger.debug("Extend cache item %s ttl to %s - ret: %s" % (key, ttl, ret))
        return ret
