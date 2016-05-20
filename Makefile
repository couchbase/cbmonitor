build: ; \
    virtualenv -p python2.7 env; \
    ./env/bin/pip install --download-cache /tmp/pip -r requirements.txt

clean: ; \
    rm -fr env; \
    rm -f `find . -name *.pyc`

flake8: ; \
    ./env/bin/flake8 --ignore=E402,E501,E731 webapp

jshint: ; \
    jshint webapp/cbmonitor/static/js/*.js

test_webapp: ; \
    ./env/bin/python webapp/manage.py test_coverage cbmonitor

test: test_webapp flake8 jshint;

update_templates: ; \
    sed -i "s|DEBUG = True|DEBUG = False|" webapp/settings.py; \
    sed -i "s|cbmonitor.db|$(CURDIR)/cbmonitor.db|" webapp/settings.py; \
    sed -i "s|MAKE_ROOT|"$(CURDIR)"|" nginx.template

run: ; \
    ./env/bin/python webapp/manage.py syncdb; \
    ./env/bin/python webapp/manage.py runserver 0.0.0.0:8000

runfcgi: update_templates; \
    kill `cat /tmp/cbmonitor.pid` ; \
    ./env/bin/python webapp/manage.py syncdb --noinput; \
    ./env/bin/python webapp/manage.py runfcgi \
        method=prefork \
        maxchildren=8 \
        minspare=2 \
        maxspare=4 \
        outlog=/tmp/cbmonitor.stdout.log \
        errlog=/tmp/cbmonitor.stderr.log \
        socket=/tmp/cbmonitor.sock \
        pidfile=/tmp/cbmonitor.pid; \
    chmod a+rw /tmp/cbmonitor.sock; \
    cp nginx.template /etc/nginx/sites-available/cbmonitor.conf; \
    ln -fs /etc/nginx/sites-available/cbmonitor.conf /etc/nginx/sites-enabled/cbmonitor.conf; \
    ln -fs $(CURDIR)/env/lib/python2.7/site-packages/django/contrib/admin/static/admin $(CURDIR)/webapp/cbmonitor/static/admin; \
    /etc/init.d/nginx reload
