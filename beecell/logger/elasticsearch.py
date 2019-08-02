# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
from datetime import datetime
from logging import Handler
import ujson as json

from beecell.simple import format_date


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
            msg[u'date'] = datetime.now() # format_date(datetime.now())
            self.client.index(index=self.index, body=msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
