import logging

from canary.util import EnvironContext

log = logging.getLogger(__name__)


class LogStashMiddleware(object):
    """
    Captures exceptions and logs them.
    Includes the URL, the exception, and the CGI/WSGI context metadata.

    :param application: the WSGI application to wrap
    :param sensitive_keys: a list of HTTP request argument names that
                           should be filtered out of debug data (e.g., CC
                           numbers and passwords)
    :param ignored_exceptions: a list of exceptions which should be ignored
    """

    DEFAULT_ERROR = """<html>
    <head><title>Internal Server Error</title></head>
    <body>
        <h1>Internal Server Error</h1>
        The server encountered an internal error or misconfiguration
        and was unable to complete your request.
    </body>
    </html>
    """

    def __init__(self, application, sensitive_keys=[], ignored_exceptions=[]):
        self.application = application
        self.sensitive_keys = sensitive_keys
        self.ignored_exceptions = ignored_exceptions

    def __call__(self, environ, start_response):
        # We want to be careful about not sending headers and the content type
        # that the app has committed to twice (if there is an exception in
        # the iterator body of the response)
        if environ.get('canary.throw_errors'):
            return self.application(environ, start_response)

        environ['canary.throw_errors'] = True
        logger = logging.LoggerAdapter(
            log,
            EnvironContext(environ, self.sensitive_keys)
        )
        environ['canary.logger'] = logger

        try:
            return self.application(environ, start_response)
        except Exception as exc:
            return self._handle_exception(environ, start_response, exc)

    def _handle_exception(self, environ, start_response, exc):
        for ignored in self.ignored_exceptions:
            if isinstance(exc, ignored):
                raise
        environ['canary.logger'].exception(exc.__class__)
        start_response(
            '500 Internal Server Error',
            [('content-type', 'text/html; charset=utf8')]
        )
        return [self.DEFAULT_ERROR]
