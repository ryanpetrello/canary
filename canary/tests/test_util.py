import unittest
import json
from cStringIO import StringIO
from wsgiref.util import setup_testing_defaults

from canary.util import EnvironContext


class TestEnvironContext(unittest.TestCase):

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
