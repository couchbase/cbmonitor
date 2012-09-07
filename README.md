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

    ./cbtop -s 10.2.1.65

    hostname        curr_items  curr_items_tot  vb_replica_curr_items  mcdMemoryAllocated  mcdMemoryReserved  memoryTotal  direct  proxy  cpu_util       swap_total
    10.2.1.67:8091  2088356     3484748         1396392                25678               25678              33657663488  11210   11211  53.634085213   10701078528
    10.2.1.68:8091  2094942     3489519         1394577                25678               25678              33657663488  11210   11211  87.9093198992  10684628992
    10.2.1.66:8091  2093029     4184065         2091036                25678               25678              33657663488  11210   11211  77.8894472362  10684628992
    10.2.1.65:8091  2088281     3477767         1389486                25678               25678              33657663488  11210   11211  63.1578947368  11350876160
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    HDD Quota:3642808487936  HDD Total:3642808487936  HDD Used:236845752483  HDD Used By Data:52853519720  RAM Quota:67108864000  RAM Total:134630653952  RAM Used:133936771072  RAM Used By Data:36040054832
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    DB Compaction:30  View Compaction:30  Min Items Threshold:10  Min Memory Threshold:10
