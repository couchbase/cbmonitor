clean: ; \
    rm -fr bin eggs develop-eggs parts .installed.cfg; \
    rm -fr collectors/cbagent.egg-info collectors/dist collectors/build; \
    rm -f `find . -name *.pyc`; \
    rm -f .coverage

build: ; \
    buildout -t 120 -q;

pep8: ; \
    ./bin/pep8 --ignore=E501 collectors webapp

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

test_collectors: ; \
    ./bin/nosetests --with-coverage --cover-package=cbagent collectors

test: build pep8 jshint test_webapp test_collectors;
