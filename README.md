cbmonitor
---------

**cbmonitor** is a web application for stats visualization and report generation.

![](docs/charts.png)

Prerequisites
-------------

* Python 2.6 or 2.7
* libcouchbase
* pip
* [seriesly](https://github.com/dustin/seriesly)

Initial setup
-------------

    $ pip install zc.buildout==1.7.0
    $ make
    $ ./bin/webapp syncdb

Running webapp
--------------

Assuming that seriesly instance is up and running:

    $ ./bin/webapp runserver
