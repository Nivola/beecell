# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

import time
import json
import logging
import multiprocessing
import threading
from beecell.simple import jsonDumps


class Event(object):
    """Event"""

    def __init__(
        self,
        event_id,
        event_type,
        data,
        transaction=None,
        user=None,
        source_addr=None,
        dest_addr=None,
    ):
        """ """
        cp = multiprocessing.current_process()
        ct = threading.current_thread()

        # event unique id
        self.id = event_id
        # event transaction id. This id can be propagated to other event to
        # trace a long operation
        self.transaction = transaction
        # fire time of event
        self.timestamp = time.strftime("%d-%m-%y %H:%M:%S", time.localtime(time.time()))
        # runtime execution process that fire event
        self.proc = "%s:%s" % (cp.ident, ct.ident)
        # user that fire event
        self.user = user
        # remote address that require event fire
        self.source_addr = source_addr
        # local address that fire event using runtime execution process
        self.dest_addr = dest_addr
        # event type like job, cmd, audit
        self.type = event_type
        # event data
        self.data = data
        # logger used to publish event
        self._logger = "beehive.event.default"

    def __str__(self):
        res = (
            "<Event id=%s, type=%s, timestamp=%s, transaction=%s, proc=%s, "
            "user=%s, source_addr=%s, dest_addr=%s, data=%s>"
            % (
                self.id,
                self.type,
                self.timestamp,
                self.transaction,
                self.proc,
                self.user,
                self.source_addr,
                self.dest_addr,
                self.data,
            )
        )
        return res

    def json(self):
        """Return json representation"""
        msg = {
            "id": self.id,
            "transaction": self.transaction,
            "timestamp": self.timestamp,
            "proc": self.proc,
            "user": self.user,
            "source_addr": self.source_addr,
            "dest_addr": self.dest_addr,
            "type": self.type,
            "data": self.data,
        }
        return jsonDumps(msg)

    def publish(self):
        """Publish new event on event logger

        When use an amqp handler for logger use this code:

            try:
                obj = Event(.....)
                obj.publish()
            except (AMQPError, Exception) as ex:
                .....
        """
        logging.getLogger(self._logger).info(self.json())

    @staticmethod
    def extract(json_event):
        """Create an Event instance from a json string"""
        data = json.loads(json_event)
        event = Event(
            data["id"],
            data["type"],
            data["data"],
            transaction=data["transaction"],
            user=data["user"],
            source_addr=data["source_addr"],
            dest_addr=data["dest_addr"],
        )
        return event


class AuditEvent(Event):
    """Job"""

    def __init__(
        self,
        event_id,
        data,
        transaction=None,
        user=None,
        source_addr=None,
        dest_addr=None,
    ):
        super(AuditEvent, self).__init__(
            event_id,
            "audit",
            data,
            transaction=transaction,
            user=user,
            source_addr=source_addr,
            dest_addr=dest_addr,
        )

        # logger used to publish event
        self._logger = "beehive.event.audit"


class JobEvent(Event):
    """Job"""

    def __init__(
        self,
        event_id,
        data,
        transaction=None,
        user=None,
        source_addr=None,
        dest_addr=None,
    ):
        super(JobEvent, self).__init__(
            event_id,
            "job",
            data,
            transaction=transaction,
            user=user,
            source_addr=source_addr,
            dest_addr=dest_addr,
        )

        # logger used to publish event
        self._logger = "beehive.event.job"
