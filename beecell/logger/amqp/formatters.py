## Copyright (c) 2009 Christopher Petrilli
##
## Permission is hereby granted, free of charge, to any person obtaining a copy of 
## this software and associated documentation files (the "Software"), to deal in 
## the Software without restriction, including without limitation the rights to 
## use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
## of the Software, and to permit persons to whom the Software is furnished to do 
## so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all 
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
## SOFTWARE.

import time
import anyjson

class JSONFormatter(object):
    """JSONFormatter provides a pluggable formatter for the Python ``logging``
    system that will turn any ``LogRecord`` into an appropriate JSON data
    structure."""

    def __init__(self, datefmt="%Y-%m-%dT%H:%M:%S",
                 appendmsec=False,
                 appendtz=False):
        """Initialize the formatter.

        Initializes the formatter with the provided date format string. If
        you want to include microseconds in the timestamp, then set
        ``appendmsec`` to True. If ``appendtz` is True, then the timezone
        information of the portal2 will also be included."""
        self.datefmt = datefmt
        self.appendmsec = appendmsec
        self.appendtz = appendtz
        
    def format(self, record):
        """Format the specified record as JSON.

        The record's attribute dictionary is serialized as JSON.  Before
        formatting the dictionary, a couple of preparatory steps are
        carried out. The message attribute of the record is computed
        using LogRecord.getMessage(). Additionally, a textual
        representation of the time is added using formatTime().
        formatException() and appended to the message.
        """
        record.message = record.getMessage()
        record.asctime = self.formatTime(record)

        return anyjson.serialize(record.__dict__)
        ##  if record.exc_info:
##             # Cache the traceback text to avoid converting it multiple times
##             # (it's constant anyway)
##             if not record.exc_text:
##                 record.exc_text = self.formatException(record.exc_info)
##         if record.exc_text:
##             if s[-1:] != "\n":
##                 s = s + "\n"
##             s = s + record.exc_text
##         return s
        

    def formatTime(self, record):
        """Return a formatted timestamp string.

        Formats the timestamp of the ``record`` according to the class
        initialization information."""
        normalized_time = time.localtime(record.created)
        timestamp = time.strftime(self.datefmt, normalized_time)

        if self.appendmsec:
            timestamp = "%s.%03d" % (timestamp, record.msecs)

        return timestamp
            
    def formatException(self, exc_info):
        pass
