import unittest

import zmq

from canary.handler import ZeroMQHandler


class ListeningTest(unittest.TestCase):

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
