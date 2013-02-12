``canary`` is a small library for recording and shipping exceptions from Python to `logstash <http://logstash.net>`_ via `ZeroMQ <http://www.zeromq.org>`_.

Example Usage
-------------

To report errors in your WSGI application, wrap your WSGI app with
``canary.middleware.LogStashMiddleware``:

.. code:: python

    from logging.config import dictConfig as load_logging_config
    from wsgiref.simple_server import make_server
    from wsgiref.util import setup_testing_defaults
    
    from canary.middleware import LogStashMiddleware
    
    
    def app(environ, start_response):
        setup_testing_defaults(environ)
        assert True is False
    
    if __name__ == '__main__':
        load_logging_config({
            'version': 1,
            'loggers': {'canary': {'level': 'DEBUG', 'handlers': ['zeromq']}},
            'handlers': {
                'zeromq': {
                    'level': 'ERROR',
                    'class': 'canary.handler.ZeroMQHandler',
                    'address': 'tcp://127.0.0.1:2120',
                    'formatter': 'logstash'
                }
            },
            'formatters': {
                'logstash': {
                    '()': 'canary.format.LogstashFormatter'
                }
            }
        })
    
        httpd = make_server('', 8080, LogStashMiddleware(app))
        print "Serving on port 8080..."
        httpd.serve_forever()
