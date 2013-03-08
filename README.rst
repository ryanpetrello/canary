``canary`` is a small library for recording and shipping exceptions from Python to `logstash <http://logstash.net>`_ via `ZeroMQ <http://www.zeromq.org>`_.

.. _travis: http://travis-ci.org/ryanpetrello/canary
.. |travis| image:: https://secure.travis-ci.org/ryanpetrello/canary.png

|travis|_

Example Usage
-------------

Assuming ``logstash`` is running and bound to a **0mq** socket at
``tcp://0.0.0.0:2120``::

    $ cat logstash.conf
    input {
        zeromq {
            type => 'python-exception'
            mode => 'server'
            topology => 'pushpull'
            address => 'tcp://0.0.0.0:2120'
            charset => 'UTF-8'
        }
    }
    output {
        debug => true
    }

...to report exceptions thrown by your WSGI application, wrap your WSGI app
with ``canary.middleware.LogStashMiddleware``:

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

Excluding Certain Exceptions
----------------------------

You may want to prevent ``canary`` from logging certain types of exceptions.
To do so, pass a list of exceptions into the ``LogStashMiddleware``
constructor:

.. code:: python

    app = LogStashMiddleware(app, ignored_exceptions=[SomePrivateException])

Filtering Sensitive Data
------------------------

``canary`` automatically populates exception logs with contextual data from the
WSGI ``environ``.  Sometimes, though, this data can contain sensitive details,
like customer's login credentials.  ``canary`` makes it easy to filter certain
request arguments from the logs it produces:

.. code:: python

    app = LogStashMiddleware(app, sensitive_keys=['password', 'cc_number'])

Development
-----------

Source hosted at `GitHub <https://github.com/ryanpetrello/canary>`_.
Report issues and feature requests on `GitHub
Issues <https://github.com/ryanpetrello/canary/issues>`_.

To fix bugs or add features to ``canary``, a GitHub account is required.

The general practice for contributing is to `fork canary
<https://help.github.com/articles/fork-a-repo>`_ and make changes in the
``next`` branch. When you're finished, `send a pull request
<https://help.github.com/articles/using-pull-requests>`_ and your patch will
be reviewed.

Tests require ``tox`` and can be run with ``$ pip install tox && tox``.

All contributions must:

* Include accompanying tests.
* Include API documentation if new features or API methods are changed/added.
* Be (generally) compliant with PEP8.
* Not break the tests or build. Before issuing a pull request, ensure that all
  tests still pass across multiple versions of Python.
