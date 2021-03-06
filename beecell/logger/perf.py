# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte

import logging
import time


class Watch(object):
    def __init__(self, f):
        self.logger = logging.getLogger(self.__class__.__module__ + '.'+self.__class__.__name__)
        
        self.cls = f.__class__
        self.name = f.__name__
        self.f = f
        self.start = time.time()
        self.current = self.start
    
    def __call__(self):
        self.start = time.time()
        res = self.f()
    
    def elapsed(self, method, msg):
        self.current = time.time()
        res = self.current - self.start
        self.logger.info("{%s::%s} %s - [%s]" % (self.user, method, msg, res))
        return "%s - [%s]" % (msg, res)
    
    def delta(self, method, msg):
        temp = time.time()
        res = temp - self.current
        self.current = temp
        self.logger.info("{%s::%s} %s - [%s]" % (self.user, method, msg, res))
        return "%s - [%s]" % (msg, res)
    
    def reset(self):
        self.start = time.time()
        self.current = self.start
    
    def resetCurrent(self):
        self.current = time.time()
