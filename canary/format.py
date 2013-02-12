import json
import logging
import re
import socket
from cStringIO import StringIO
from contextlib import closing


class LogstashFormatter(logging.Formatter):
    """
    A custom JSON formatter intended for consumption by logstash
    """

    DEFAULT_KEYS = ['fields']

    def __init__(self, keys=DEFAULT_KEYS, *args, **kwargs):
        log_format = ' '.join(['%({0})'] * len(keys))
        custom_format = log_format.format(*keys)

        logging.Formatter.__init__(
            self,
            fmt=custom_format,
            *args,
            **kwargs
        )

    def parse(self):
        standard_formatters = re.compile(r'\((.*?)\)', re.IGNORECASE)
        return standard_formatters.findall(self._fmt)

    def serialize(self, record):
        formatters = self.parse()
        record.message = record.getMessage()

        log_record = {
            '@message': record.message,
            '@source_host': socket.gethostname(),
        }
        if getattr(record, 'exc_info', None):
            log_record['traceback'] = self.formatException(record.exc_info)

        for formatter in formatters:
            if formatter in record.__dict__:
                log_record[formatter] = record.__dict__[formatter]

        return log_record

    def format(self, record):
        """Formats a log record and serializes to JSON"""
        record = self.serialize(record)

        class PyObjectEncoder(json.JSONEncoder):
            """
            Because we're not actually decoding this on the other end,
            we really just want JSON serialization.  For non-native types we
            can't JSON-serialize, strings will work just fine as a fallback.
            """
            def default(self, obj):
                return str(obj)

        with closing(StringIO()) as output:
            for c in PyObjectEncoder().iterencode(record):
                output.write(c)
            return output.getvalue()
