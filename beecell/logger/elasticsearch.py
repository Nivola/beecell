# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

import logging
from datetime import datetime
from logging import Handler, Formatter
import json


logger = logging.getLogger(__name__)


class ElasticsearchFormatter(Formatter):
    def format(self, record):
        """
        Format the specified record as text.

        The record's attribute dictionary is used as the operand to a
        string formatting operation which yields the returned string.
        Before formatting the dictionary, a couple of preparatory steps
        are carried out. The message attribute of the record is computed
        using LogRecord.getMessage(). If the formatting string uses the
        time (as determined by a call to usesTime(), formatTime() is
        called to format the event time. If there is exception information,
        it is formatted using formatException() and appended to the message.
        """
        try:
            message = record.message
        except:
            logger.warning(type(record))
        record.message = ""

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        try:
            s = self._fmt % record.__dict__
        except UnicodeDecodeError as e:
            # Issue 25664. The logger name may be Unicode. Try again ...
            try:
                record.name = record.name.decode("utf-8")
                s = self._fmt % record.__dict__
            except UnicodeDecodeError:
                raise e
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        # create main record
        s = json.loads(s)

        # add exception trace to error message
        if record.exc_text:
            message += " | " + record.exc_text

        # add message to fianle record
        s["message"] = message
        # StringFormatter().replace(message)

        return s


class ElasticsearchHandler(Handler):
    def __init__(self, client, index="log", tags=[], **custom_fields):
        """Initialize the handler.

        :param client: elasticsearch.Elasticsearch class instance
        :param index: elasticsearch index name
        :param tags: list of tags to add [optional]
        :param custom_fields: custom fields as key=value
        """
        Handler.__init__(self)

        if client is None:
            raise Exception("elasticsearch.Elasticsearch class instance must be specified")

        from elasticsearch import Elasticsearch

        self.elasticsearch: Elasticsearch = client
        self.index = index
        self.tags = tags
        self.custom_fields = custom_fields
        self.request_timeout = 30

    def _emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        record.api_id = getattr(record, "api_id", "")
        
        msg = self.format(record)
        date = datetime.now()
        msg["date"] = date
        msg["tags"] = self.tags
        msg.update(self.custom_fields)

        # ex. logstash-2024.03.23
        index = "%s-%s" % (self.index, date.strftime("%Y.%m.%d"))
        logger.debug("_emit - index: %s" % index)

        # self.client.index(index=index, body=msg, request_timeout=30, doc_type="doc")
        self.elasticsearch._request_timeout = 30
        self.elasticsearch.index(index=index, body=msg)

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        import gevent

        try:
            gevent.spawn(self._emit, record)
            # self._emit(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
