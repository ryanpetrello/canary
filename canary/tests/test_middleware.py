import json
import logging
from wsgiref.util import setup_testing_defaults

from canary.format import LogstashFormatter
from canary.middleware import LogStashMiddleware
from canary.tests import ListeningTest


class TestMiddleware(ListeningTest):

    def setUp(self):
        super(TestMiddleware, self).setUp()
        log = logging.getLogger('canary')
        log.addHandler(self.handler)
        log.setLevel(logging.DEBUG)
        self.handler.setFormatter(LogstashFormatter())

    @property
    def app(self):
        def a(environ, start_response):
            raise Exception('Example Error')
        return a

    def _make_request(self, environ=None, **kw):
        environ = environ or {}
        setup_testing_defaults(environ)

        def start_response(status, response_headers, exc_info=None):
            pass

        list(LogStashMiddleware(self.app)(
            environ,
            start_response
        ))
        return environ

    def test_simple_exception(self):
        self._make_request()
        record = json.loads(self.listener.recv())
        assert 'Exception: Example Error' in record['traceback']
        for header in (
            'HTTP_HOST', 'PATH_INFO', 'REQUEST_METHOD', 'SERVER_NAME',
            'SERVER_PORT', 'SERVER_PROTOCOL'
        ):
            assert header in record['fields']['CGI Variables']
        assert 'WSGI Variables' in record['fields']


class IgnoredException(Exception):
    pass


class TestIgnoredExceptions(TestMiddleware):

    @property
    def app(self):
        def a(environ, start_response):
            raise IgnoredException('Ignored')
        return a

    def _make_request(self, environ=None, **kw):
        environ = environ or {}
        setup_testing_defaults(environ)

        def start_response(status, response_headers, exc_info=None):
            pass  # pragma: nocover

        list(LogStashMiddleware(self.app, ignored_exceptions=[IgnoredException])(
            environ,
            start_response
        ))

    def test_simple_exception(self):
        self.assertRaises(
            IgnoredException,
            self._make_request
        )
