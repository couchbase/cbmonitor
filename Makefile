build: ; \
    buildout -t 120 -q

clean: ; \
    rm -fr bin eggs develop-eggs parts .installed.cfg; \
    rm -f `find . -name *.pyc`

pep8: ; \
    ./bin/pep8 --ignore=E501 webapp

jshint: ; \
    jshint webapp/cbmonitor/static/scripts/charts.js \
           webapp/cbmonitor/static/scripts/dialogs.js \
           webapp/cbmonitor/static/scripts/graph.js \
           webapp/cbmonitor/static/scripts/inventory.js \
           webapp/cbmonitor/static/scripts/observables.js \
           webapp/cbmonitor/static/scripts/seriesly.js \
           webapp/cbmonitor/static/scripts/snapshots.js \
           webapp/cbmonitor/static/scripts/views.js

test_webapp: ; \
    ./bin/webapp test_coverage cbmonitor

test: pep8 jshint test_webapp;

update_templates: ; \
    sed -i "s|DEBUG = True|DEBUG = False|" webapp/settings.py; \
    sed -i "s|cbmonitor.db|$(CURDIR)/cbmonitor.db|" webapp/settings.py; \
    sed -i "s|MAKE_ROOT|"$(CURDIR)"|" nginx.template

run_fcgi: update_templates; \
    killall -q webapp; \
    ./bin/webapp syncdb --noinput; \
    ./bin/webapp runfcgi method=threaded socket=/tmp/cbmonitor.sock; \
    chmod a+rw /tmp/cbmonitor.sock; \
    cp nginx.template /etc/nginx/sites-available/cbmonitor; \
    ln -fs /etc/nginx/sites-available/cbmonitor /etc/nginx/sites-enabled/cbmonitor; \
    /etc/init.d/nginx reload
