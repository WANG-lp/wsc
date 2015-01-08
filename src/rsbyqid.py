
import random
import sys
import collections

db = collections.defaultdict(list)

for ln in sys.stdin:
	db[tuple(ln.split(" ", 2)[:2])] += [ln.strip()]

for qid, lns in db.iteritems():
	print "\n".join(random.sample(lns, min(len(lns), int(sys.argv[1]))))
