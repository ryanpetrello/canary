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
            'loggers': {'canary': {'level': 'ERROR', 'handlers': ['zeromq']}},
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

::

    ~/canary $ python demo.py
    Serving on port 8080...
    ^Z
    zsh: suspended  python demo.py
    ~/canary $ bg
    [1]  - continued  python demo.py
    ~/canary $ curl -I "http://localhost:8080/"
    HTTP/1.0 500 Internal Server Error
    Date: Tue, 12 Feb 2013 22:56:46 GMT
    Server: WSGIServer/0.1 Python/2.7.2
    content-type: text/html; charset=utf8
    Content-Length: 334
    
    1.0.0.127.in-addr.arpa - - [12/Feb/2013 17:56:46] "HEAD / HTTP/1.1" 500 334
