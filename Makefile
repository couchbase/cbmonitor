clean:
	rm -fr bin eggs develop-eggs parts .installed.cfg
	rm -fr cbtop/cbtop.egg-info
	rm -f MemcachedSource-*.json cbtop.log
	rm -fr priority15/priority15.egg-info
	rm -fr cbagent/cbagent.egg-info cbagent/dist cbagent/build
	rm -f `find . -name *.pyc`
