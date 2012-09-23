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

    pip install django-http-proxy

    pip install httplib2

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

    DB Compaction: 30.00  View Compaction: 30.00  Min Items Threshold: 10  Min Memory Threshold: 10  Compact Running: False  Disk Format Ver: 0


    HDD Quota: 3.31T  HDD Total: 3.31T  HDD Used: 33.93G  HDD Used By Data: 933.66M  RAM Quota: 62.50G  RAM Total: 125.38G  RAM Used: 57.06G 
    RAM Used By Data: 992.36M


    BUCKET   PROXY  RAM     RAW_RAM   #REPL  DATA_USED  DISK_USED  #ITEMS   #MEM_USED  %MEM_USED  TYPE   
    bucket1  0      7.81G   1.95G     1      187.00K    16.21M     0.00     59.98M     0.75       membase
    bucket2  0      7.81G   1.95G     1      187.00K    16.21M     0.00     59.98M     0.30       membase
    bucket3  0      19.53G  4.88G     1      731.03M    885.03M    147.43K  812.43M    20.31      membase
    default  0      3.91G   1000.00M  1      187.00K    16.21M     0.00     59.97M     0.75       membase


    HOST            #ITEMS  #ITEMS_TOT  #REPL_ITEMS  MCD_MEM_ALLOC  MCD_MEM_RSVD  MEM_FREE  MEM_TOT  PORT   STATUS   %CPU  SWAP_TOT  SWAP_USED
    10.2.1.65:8091  0.00    49.24K      49.24K       25678.00       25678.00      17.02G    31.35G   11210  healthy  3.75  10.57G    148.00K  
    10.2.1.66:8091  65.80K  82.04K      16.25K       25678.00       25678.00      17.04G    31.35G   11210  healthy  5.49  9.95G     148.00K  
    10.2.1.67:8091  81.63K  98.10K      16.47K       25678.00       25678.00      16.93G    31.35G   11210  healthy  5.01  9.97G     148.00K  
    10.2.1.68:8091  0.00    65.47K      65.47K       25678.00       25678.00      17.34G    31.35G   11210  healthy  7.25  9.95G     148.00K 
