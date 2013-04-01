from setuptools import setup, find_packages

version = '0.1.3'

#
# determine requirements
#
requirements = ['pyzmq']
tests_require = []

setup(
    name='canary',
    version=version,
    description=("canary is a small library for recording and shipping "
                 "exceptions from Python to logstash via ZeroMQ."),
    long_description="",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],
    keywords='web framework wsgi logstash logging zeromq',
    author='Ryan Petrello',
    author_email='ryan@ryanpetrello.com',
    url='http://github.com/ryanpetrello/canary',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    tests_require=tests_require,
    test_suite='canary'
)
