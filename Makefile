clean: ; \
    rm -fr bin eggs develop-eggs parts .installed.cfg; \
    rm -fr cbtop/cbtop.egg-info; \
    rm -f MemcachedSource-*.json cbtop.log; \
    rm -fr priority15/priority15.egg-info; \
    rm -fr collectors/cbagent.egg-info collectors/dist collectors/build; \
    rm -f `find . -name *.pyc`

test: ; \
    buildout -t 120 -q; \
    ./bin/django test_coverage cbmonitor; \
    ./bin/pep8 --ignore=E501 collectors cbtop priority15 webapp; \
    jshint webapp/cbmonitor/static/scripts
