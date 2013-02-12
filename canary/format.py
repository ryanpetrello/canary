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

    def serialize(self, record):
        formatters = self.parse()
        record.message = record.getMessage()

        log_record = {
            '@message': record.message,
            '@source_host': socket.gethostname(),
            'traceback': self.formatException(record.exc_info)
        }

        for formatter in formatters:
            log_record[formatter] = record.__dict__[formatter]

        return log_record

    def format(self, record):
        """Formats a log record and serializes to JSON"""
        record = self.serialize(record)

        # Compile an regex of OR'ed strings to filter out
        sensitive_values_re = re.compile(
            '|'.join([re.escape(v) for v in []])
        )

        #
        # Compile a regex for single punctuation characters
        # We'll use this to avoid filtering out user input which represents
        # JSON structure, e.g., {, :, }
        #
        punctuation_re = re.compile('^[^0-9a-zA-Z]$')

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
                if sensitive_values_re.pattern and not punctuation_re.match(c):
                    c = sensitive_values_re.sub('********', c)
                output.write(c)
            return output.getvalue()
