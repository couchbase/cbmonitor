Prerequisites
-------------

* Python 2.6
* pip

Dependencies
------------

    pip install django==1.4.1

    pip install docutils

    pip install lettuce

    pip install nose

    pip install blessings

    pip install numpy

Web application setup
---------------------

    python webapp/manage.py syncdb

    python webapp/manage.py runserver 0.0.0.0:8000

Testing
-------

    python webapp/manage.py harvest -d webapp

    lettuce whisper

virtualenv tips
---------------

    virtualenv -p python2.6 --no-site-packages priority15

    source priority15/bin/activate

    ...

    deactivate

Logging
--------

    Use standard python logging component

    Configuration file: logging.conf
