import json
import logging
import re
import socket
import traceback
from cStringIO import StringIO
from contextlib import closing


class LogstashFormatter(logging.Formatter):
    """
    A custom JSON formatter intended for consumption by logstash
    """

    def __init__(self, keys=['message', 'fields'], *args, **kwargs):
        log_format = ' '.join(['%({})'] * len(keys))
        custom_format = log_format.format(*keys)

        super(LogstashFormatter, self).__init__(
            fmt=custom_format,
            *args,
            **kwargs
        )

    def parse(self):
        standard_formatters = re.compile(r'\((.*?)\)', re.IGNORECASE)
        return standard_formatters.findall(self._fmt)

    def format(self, record):
        """Formats a log record and serializes to JSON"""

        formatters = self.parse()

        record.message = record.getMessage()

        log_record = {}
        for formatter in formatters:
            log_record[formatter] = record.__dict__[formatter]

        log_record.update({
            '@message': record.message,
            '@source_host': socket.gethostname(),
            'traceback': ''.join(
                traceback.format_exception(*record.exc_info)
            )
        })

        class PyObjectEncoder(json.JSONEncoder):
            """
            Because we're not actually decoding this on the other end,
            we really just want JSON serialization.  For non-native types we
            can't JSON-serialize, strings will work just fine as a fallback.
            """
            def default(self, obj):
                return str(obj)

        with closing(StringIO()) as output:
            for chunk in PyObjectEncoder().iterencode(log_record):
                output.write(chunk)
            return output.getvalue()
