import logging
import json

from canary.format import LogstashFormatter
from canary.tests import ListeningTest


class TestLogging(ListeningTest):

    def test_basic_logging(self):
        log = logging.getLogger()
        log.addHandler(self.handler)
        log.setLevel(logging.DEBUG)

        log.info("Hello, World!")
        assert self.listener.recv() == "Hello, World!"

    def test_logstash_format(self):
        self.handler.setFormatter(LogstashFormatter())
        log = logging.getLogger()
        log.addHandler(self.handler)
        log.setLevel(logging.DEBUG)

        log.info("Hello, World!")
        record = json.loads(self.listener.recv())
        assert record.keys() == ['@source_host', '@message']
        assert record['@message'] == 'Hello, World!'

    def test_logstash_format_exception(self):
        self.handler.setFormatter(LogstashFormatter())
        log = logging.getLogger()
        log.addHandler(self.handler)
        log.setLevel(logging.DEBUG)

        try:
            raise Exception("Example Error")
        except Exception as e:
            log.exception(e)

        record = json.loads(self.listener.recv())
        assert 'traceback' in record
        assert 'Exception: Example Error' in record['traceback']
