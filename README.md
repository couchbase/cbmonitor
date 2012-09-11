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

    pip install tabula

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
-------

Use standard python logging component. Configuration file is **logging.conf**.

cbtop
-------

Cbtop tells you about a couchbase cluster.

Simply point it to one of the servers:

    ./cbtop 10.2.1.65

    hostname        curr_items  curr_items_tot  vb_replica_curr_items  mcdMemoryAllocated
    mcdMemoryReserved  memoryTotal  direct  cpu_util       swap_total

    10.2.1.66:8091  4.79M       9.58M           4.79M                  25678
    25678              31.35G       11210   11.5           9.95G

    10.2.1.67:8091  4.79M       9.58M           4.79M                  25678
    25678              31.35G       11210   16.5           9.97G

    10.2.1.65:8091  4.79M       9.58M           4.79M                  25678
    25678              31.35G       11210   13.4663341646  10.57G

    10.2.1.68:8091  4.79M       9.58M           4.79M                  25678
    25678              31.35G       11210   14.5           9.95G


    ---------------------------------------------------------------------------------------------
    HDD Quota:3642808487936  HDD Total:3.31T  HDD Used:127.25G  HDD Used By Data:100.62G
    RAM Quota:78.12G  RAM Total:125.38G  RAM Used:124.73G  RAM Used By Data:56.53G


    ---------------------------------------------------------------------------------------------
    DB Compaction:30  View Compaction:30  Min Items Threshold:10  Min Memory Threshold:10
