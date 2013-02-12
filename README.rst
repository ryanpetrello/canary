``canary`` is a small library for recording and shipping exceptions from Python to `logstash <http://logstash.net>`_ via `ZeroMQ <http://www.zeromq.org>`_.

Example Usage
-------------
.. code:: python

    import argparse
    import logging
    from wsgiref.simple_server import make_server
    from wsgiref.util import setup_testing_defaults
    
    from canary.format import LogstashFormatter
    from canary.handler import ZeroMQHandler
    from canary.middleware import LogStashMiddleware
    
    
    def app(environ, start_response):
        setup_testing_defaults(environ)
        assert True is False
    
    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--address',
            action="store",
            default='tcp://127.0.0.1:2120'
        )
    
        log = logging.getLogger('canary')
        handler = ZeroMQHandler(**vars(parser.parse_args()))
        handler.setFormatter(LogstashFormatter())
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)
    
        httpd = make_server('', 8080, LogStashMiddleware(app))
        print "Serving on port 8080..."
        httpd.serve_forever()
