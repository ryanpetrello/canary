import logging
import threading

import zmq


class ZeroMQHandler(logging.Handler):

    def __init__(self, address="tcp://127.0.0.1:2120", context=None,
                 *args, **kwargs):
        logging.Handler.__init__(self)
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
        self.publisher.send_unicode(data)

    def emit(self, record):
        self._send(self.format(record))
