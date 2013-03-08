import unittest
import json
from cStringIO import StringIO
from wsgiref.util import setup_testing_defaults

from canary.util import EnvironContext


class TestEnvironContext(unittest.TestCase):

    def test_GET_params(self):
        params = EnvironContext.params({
            'QUERY_STRING': 'a=1&b=2',
            'wsgi.input': StringIO()
        })
        assert params['a'] == ['1']
        assert params['b'] == ['2']

    def test_multiple_GET_params(self):
        params = EnvironContext.params({
            'QUERY_STRING': 'a=1&a=2&b=3',
            'wsgi.input': StringIO()
        })
        assert params['a'] == ['1', '2']
        assert params['b'] == ['3']

    def test_POST_params(self):
        params = 'a=1&b=2'
        io = StringIO()
        io.write(params)
        io.seek(0)

        params = EnvironContext.params({
            'REQUEST_METHOD': 'POST',
            'QUERY_STRING': '',
            'CONTENT_LENGTH': len(params),
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'wsgi.input': io
        })
        assert params['a'] == ['1']
        assert params['b'] == ['2']

    def test_multiple_POST_params(self):
        params = 'a=1&a=2&b=3'
        io = StringIO()
        io.write(params)
        io.seek(0)

        params = EnvironContext.params({
            'REQUEST_METHOD': 'POST',
            'QUERY_STRING': '',
            'CONTENT_LENGTH': len(params),
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'wsgi.input': io
        })
        assert params['a'] == ['1', '2']
        assert params['b'] == ['3']

    def test_mixed_params(self):
        params = 'a=1&a=2&b=3'
        io = StringIO()
        io.write(params)
        io.seek(0)

        params = EnvironContext.params({
            'REQUEST_METHOD': 'POST',
            'QUERY_STRING': 'a=4&b=5',
            'CONTENT_LENGTH': len(params),
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'wsgi.input': io
        })
        assert len(params['a']) == 3
        assert '1' in params['a']
        assert '2' in params['a']
        assert '4' in params['a']
        assert len(params['b']) == 2
        assert '3' in params['b']
        assert '5' in params['b']

    def test_filter_sensitive_keys(self):
        POST = 'password=abc123&cc_number=4111111111111111&foo=bar'
        io = StringIO()
        io.write(POST)
        io.seek(0)
        context = EnvironContext({
            'QUERY_STRING': 'password=secret&spam=eggs',
            'CONTENT_LENGTH': len(POST),
            'wsgi.input': io
        }, ('password', 'cc_number'))
        raw = json.dumps(context.filtered_environ)
        assert 'abc123' not in raw
        assert '4111111111111111' not in raw
        assert 'secret' not in raw

    def test_context_excludes_os_environ_variables(self):
        environ = {}
        setup_testing_defaults(environ)
        environ.update({'HOME': '/home/john'})
        context = EnvironContext(environ)
        assert 'HOME' not in context['fields']['CGI Variables']
