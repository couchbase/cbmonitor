# Relationship between files...
#   stats.org
#     ==> [automated cleansing (make stats.org.gen)] ==>
#   stats.org.gen
#     ==> [manual annotation (cp stats.org.gen stats.src && emacs stats.src)] ==>
#   stats.src
#     ==> [json conversion (stats-conv.py stats.src)] ==>
#   stats.json
#
all: stats.org.gen stats.json

clean:
	rm -f stats.org stats.org.gen stats.json

stats.org:
	wget https://raw.github.com/couchbase/ep-engine/master/docs/stats.org

stats.org.gen: stats.org
	cat stats.org | \
      grep -E "(^[|*])|(engine:)" | grep -v "\-\-\-\-\-\-\-" | \
	  grep -v "Stats Definitions" | grep -v "Getting Started" | grep -v "Description" \
    > stats.org.gen

stats.json: stats.src
	./stats-conv.py stats.src > stats.json

diff:
	grep -v "^  " stats.src | diff stats.org.gen -

