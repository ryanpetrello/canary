import os
import re
import cgi
import tempfile
from urlparse import parse_qs

from wsgiref.util import guess_scheme


def cachedproperty(f):
    """returns a cached property that is calculated by function f"""
    def get(self):
        try:
            return self._property_cache[f]
        except AttributeError:
            self._property_cache = {}
            x = self._property_cache[f] = f(self)
            return x
        except KeyError:
            x = self._property_cache[f] = f(self)
            return x
    return property(get)


class EnvironContext(object):

    def __init__(self, environ, sensitive_keys=[]):
        """
        Compose additional information about the CGI and WSGI environment.

        :param environ: the WSGI environ for the request
        :param sensitive_keys: a list of HTTP request argument names that
                               should be filtered out of debug data (e.g., CC
                               numbers and passwords)
        """
        self._environ = environ
        self._sensitive_keys = sensitive_keys

    @cachedproperty
    def _metadata(self):
        environ = self.filtered_environ
        data = {}
        data['HTTP_SCHEME'] = guess_scheme(environ)
        cgi_vars = data['CGI Variables'] = {}
        wsgi_vars = data['WSGI Variables'] = {}
        hide_vars = ['wsgi.errors', 'wsgi.input',
                     'wsgi.multithread', 'wsgi.multiprocess',
                     'wsgi.run_once', 'wsgi.version',
                     'wsgi.url_scheme', 'webob._parsed_cookies']
        for name, value in environ.items():
            if name.upper() == name:
                if name in os.environ:  # Skip OS environ variables
                    continue
                if value:
                    cgi_vars[name] = value
            elif name not in hide_vars:
                wsgi_vars[name] = value
        proc_desc = tuple([int(bool(environ[key]))
                           for key in ('wsgi.multiprocess',
                                       'wsgi.multithread',
                                       'wsgi.run_once')])
        wsgi_vars['wsgi process'] = self.process_combos[proc_desc]
        return {'fields': data, 'filter_sensitive': self._filter_sensitive}

    @cachedproperty
    def sensitive_values(self):
        """
        Returns a list of sensitive GET/POST values to filter from logs.
        """
        values = set()
        params = EnvironContext.params(self._environ)
        for key in self._sensitive_keys:
            if key in params:
                values |= set(params[key])
        return values

    def __getitem__(self, name):
        return self._metadata.__getitem__(name)

    def __iter__(self):
        return self._metadata.__iter__()

    process_combos = {
        # multiprocess, multithread, run_once
        (0, 0, 0): 'Non-concurrent server',
        (0, 1, 0): 'Multithreaded',
        (1, 0, 0): 'Multiprocess',
        (1, 1, 0): 'Multi process AND threads (?)',
        (0, 0, 1): 'Non-concurrent CGI',
        (0, 1, 1): 'Multithread CGI (?)',
        (1, 0, 1): 'CGI',
        (1, 1, 1): 'Multi thread/process CGI (?)',
    }

    @classmethod
    def params(cls, environ):
        """
        Given a WSGI environ context, returns a list of mapping of parsed GET
        and POST variables.
        """
        environ = environ.copy()
        params = parse_qs(environ.get('QUERY_STRING', ''))

        environ['QUERY_STRING'] = ''
        fp, length = EnvironContext._copy_body_to_tempfile(environ)
        environ.setdefault('CONTENT_LENGTH', length)

        fs = cgi.FieldStorage(
            fp=fp,
            environ=environ,
            keep_blank_values=True
        )

        for k in fs:
            if k in params:
                params[k].extend(fs.getlist(k))
            else:
                params[k] = fs.getlist(k)

        return params

    @classmethod
    def _copy_body_to_tempfile(cls, environ):
        """
        Copy wsgi.input to a tempfile so it can be reused.
        """
        try:
            length = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            length = 0

        fileobj = tempfile.SpooledTemporaryFile(1024*1024)
        if length:
            remaining = length
            while remaining > 0:
                data = environ['wsgi.input'].read(min(remaining, 65536))
                if not data:
                    raise IOError(
                        "Client disconnected (%s more bytes were expected)"
                        % remaining
                    )
                fileobj.write(data)
                remaining -= len(data)

        fileobj.seek(0)
        environ['wsgi.input'] = fileobj
        return fileobj, length

    @property
    def filtered_environ(self):
        """
        A WSGI environ with which has had sensitive values filtered
        """
        return self._filter_sensitive(self._environ)

    def _filter_sensitive(self, value):
        # Compile an regex of OR'ed strings to filter out
        sensitive_values_re = re.compile(
            '|'.join([
                re.escape(v)
                for v in self.sensitive_values
            ])
        )

        def _gen(o):
            def _filter(string):
                if sensitive_values_re.pattern:
                    return sensitive_values_re.sub('********', string)
                return string
            if isinstance(o, basestring):
                return _filter(o)
            elif isinstance(o, (list, tuple)):
                return [
                    _gen(x)
                    for x in o
                ]
            elif isinstance(o, dict):
                return dict(
                    (k, _gen(v))
                    for k, v in o.items()
                )
            else:
                return _filter(str(o))
        return _gen(value)
