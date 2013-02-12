import os

from wsgiref.util import guess_scheme


class EnvironContext(object):

    def __init__(self, environ):
        self._environ = environ

    @property
    def metadata(self):
        """
        Compose additional information about the CGI and WSGI environment.

        :param environ: the WSGI environ for the request
        """
        data = {}
        data['HTTP_SCHEME'] = guess_scheme(self._environ)
        cgi_vars = data['CGI Variables'] = {}
        wsgi_vars = data['WSGI Variables'] = {}
        hide_vars = ['wsgi.errors', 'wsgi.input',
                     'wsgi.multithread', 'wsgi.multiprocess',
                     'wsgi.run_once', 'wsgi.version',
                     'wsgi.url_scheme', 'webob._parsed_cookies']
        for name, value in self._environ.items():
            if name.upper() == name:
                if name in os.environ:  # Skip OS environ variables
                    continue
                if value:
                    cgi_vars[name] = value
            elif name not in hide_vars:
                wsgi_vars[name] = value
        if self._environ['wsgi.version'] != (1, 0):
            wsgi_vars['wsgi.version'] = self._environ['wsgi.version']
        proc_desc = tuple([int(bool(self._environ[key]))
                           for key in ('wsgi.multiprocess',
                                       'wsgi.multithread',
                                       'wsgi.run_once')])
        wsgi_vars['wsgi process'] = self.process_combos[proc_desc]
        return {'fields': data}

    def __getitem__(self, name):
        return self.metadata.__getitem__(name)

    def __iter__(self):
        return self.metadata.__iter__()

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
