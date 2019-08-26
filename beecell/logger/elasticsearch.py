# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

import urllib
from datetime import datetime
from logging import Handler, Formatter
from re import escape
import sys
import ujson as json
# import json

from beecell.simple import format_date


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
        message = record.message
        message = message.replace('\"', "'")
        record.message = message

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        try:
            s = self._fmt % record.__dict__
        except UnicodeDecodeError as e:
            # Issue 25664. The logger name may be Unicode. Try again ...
            try:
                record.name = record.name.decode('utf-8')
                s = self._fmt % record.__dict__
            except UnicodeDecodeError:
                raise e
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            try:
                s = s + record.exc_text
            except UnicodeError:
                # Sometimes filenames have non-ASCII chars, which can lead
                # to errors when s is Unicode and record.exc_text is str
                # See issue 8924.
                # We also use replace for when there are multiple
                # encodings, e.g. UTF-8 for the filesystem and latin-1
                # for a script. See issue 13232.
                s = s + record.exc_text.decode(sys.getfilesystemencoding(), 'replace')
        return s


class ElasticsearchHandler(Handler):
    def __init__(self, client, index=u'log'):
        """Initialize the handler.

        :param client: elasticsearch.Elasticsearch class instance
        :param index: elasticsearch index name
        """
        Handler.__init__(self)

        if client is None:
            raise Exception(u'elasticsearch.Elasticsearch class instance must be specified')

        self.client = client
        self.index = index

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
        try:
            msg = self.format(record)
            msg = json.loads(msg)
            date = datetime.now()
            msg[u'date'] = date
            # ex. logstash-2024.03.23
            index = u'%s-%s' % (self.index, date.strftime(u'%Y.%m.%d'))
            self.client.index(index=index, body=msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
