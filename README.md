cbmonitor
---------

**cbmonitor** is a web application for stats visualization and report generation.

![](docs/charts.png)

Prerequisites
-------------

* Python 2.7 (including headers)
* virtualenv
* libcouchbase
* libfreetype-devel (or equivalent)
* libatlas-devel (or equivalent)
* [seriesly](https://github.com/dustin/seriesly)

Initial setup
-------------

    $ make

Running webapp
--------------

Assuming that seriesly instance is up and running:

    $ make run
