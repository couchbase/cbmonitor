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

    DB Compaction:30.00  View Compaction:30.00  Min Items Threshold:10  Min Memory Threshold:10  Compact Running:False  Disk Format Ver:0

    HDD Quota:2.75T  HDD Total:2.75T  HDD Used:267.59G  HDD Used By Data:119.97G  RAM Quota:97.66G  RAM Total:125.38G  RAM Used:124.77G  RAM Used By Data:71.10G

    BUCKET   PROXY  RAM     RAW_RAM  #REPL  DATA_USED  DISK_USED  #ITEMS  #MEM_USED  %MEM_USED  TYPE
    default  0      97.66G  24.41G   1      90.57G     119.97G    19.16M  71.09G     72.80      membase

    HOST            #ITEMS  #ITEMS_TOT  #REPL_ITEMS  MCD_MEM_ALLOC  MCD_MEM_RSVD  MEM_FREE  MEM_TOT  PORT   STATUS   %CPU   SWAP_TOT  SWAP_USED
    10.2.1.65:8091  4.79M   9.58M       4.79M        25678.00       25678.00      158.47M   31.35G   11210  healthy  48.38  10.57G    156.00K
    10.2.1.66:8091  4.79M   9.58M       4.79M        25678.00       25678.00      156.31M   31.35G   11210  healthy  78.39  9.95G     156.00K
    10.2.1.67:8091  4.79M   9.58M       4.79M        25678.00       25678.00      157.81M   31.35G   11210  healthy  91.25  9.97G     156.00K
    10.2.1.68:8091  4.79M   9.58M       4.79M        25678.00       25678.00      153.09M   31.35G   11210  healthy  99.25  9.95G     156.00K

    HOST       #ERR_OOM  EP_OVERHEAD  TCM_MAX_TCACHE  EP_MAX_DATA  EP_LOW_WAT  EP_HIGH_WAT  EP_VAL  #ERR_TMP_OOM  TCM_UNMAPPED  EP_BYTES_TOT  TCM_CUR_TCACHE  EP_KV
    10.2.1.65  0.00      51.79M       4.00M           24.41G       14.65G      18.31G       16.57G  0.00          28.95M        17.65G        2.53M           17.35G
    10.2.1.66  0.00      51.62M       4.00M           24.41G       14.65G      18.31G       16.64G  0.00          33.59M        17.71G        2.17M           17.41G
    10.2.1.67  0.00      51.64M       4.00M           24.41G       14.65G      18.31G       16.46G  0.00          26.48M        17.54G        2.05M           17.23G
    10.2.1.68  0.00      52.12M       4.00M           24.41G       14.65G      18.31G       17.12G  0.00          21.84M        18.20G        2.71M           17.89G

    Last Update: 18:06:01
