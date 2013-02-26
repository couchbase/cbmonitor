Prerequisites
-------------

* Python 2.6 or 2.7
* matplotlib
* pip
* [seriesly](https://github.com/dustin/seriesly)

Dependencies
------------

    $ pip install zc.buildout==1.7.0

General setup
-------------

    $ make build

Running webapp
--------------

Assuming that seriesly instance is up and running:

    $ ./bin/webapp syncdb
    $ ./bin/webapp runserver

Running collectors via CLI:
---------------------------

    $ ./bin/ns_collector sample.cfg

Running tests
-------------

    $ make test
