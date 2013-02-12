import unittest
import logging
import json

import zmq

from canary.handler import ZeroMQHandler
from canary.format import LogstashFormatter


class TestLogging(unittest.TestCase):

    def setUp(self):
        self.context = zmq.Context.instance()

        self.listener = zmq.Socket(self.context, zmq.SUB)
        self.listener.setsockopt(zmq.LINGER, 0)
        self.listener.setsockopt(
            zmq.SUBSCRIBE,
            zmq.utils.strtypes.asbytes('')
        )

        self.port = self.listener.bind_to_random_port("tcp://127.0.0.1")
        self.handler = ZeroMQHandler(
            "tcp://127.0.0.1:{0}".format(self.port),
            context=self.context
        )
        self.handler.publisher.setsockopt(zmq.LINGER, 0)

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
