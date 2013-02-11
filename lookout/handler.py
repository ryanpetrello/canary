import json
import logging
import socket
import threading
from datetime import datetime

import zmq


class ZeroMQHandler(logging.Handler):

    def __init__(self, address="tcp://127.0.0.1:2120", context=None):
        super(ZeroMQHandler, self).__init__()
        import pdb; pdb.set_trace()
        self._address = address
        self._context = context
        if context is None:
            self._context = zmq.Context.instance()
        # 0mq sockets aren't threadsafe; bind them to a threadlocal
        self._local = threading.local()

    @property
    def publisher(self):
        if not hasattr(self._local, 'publisher'):
            self._local.publisher = self._context.socket(zmq.PUSH)
            self._local.publisher.connect(self._address)
        return self._local.publisher

    def _send(self, data):
        self.publisher.send_unicode(json.dumps(data))

    def emit(self, record):
        data = {
            '@timestamp': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            '@source_host': socket.gethostname(),
            '@message': record.msg,
            '@fields': []
        }
        self._send(data)
