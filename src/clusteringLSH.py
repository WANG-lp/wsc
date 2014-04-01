
import sys
import collections
import itertools

cluster = collections.defaultdict(list)

for ln in open(sys.argv[1]):
	try:
		# p1, p2, arg, sentdist, c1, c2, t1, t2, src, h = ln.strip().split("\t")
		p1, h = ln.strip().split("\t")
		h     = h[:int(sys.argv[2])]

	except ValueError:
		continue

	for pos in itertools.combinations(range(len(h)), int(sys.argv[3])):
		cluster[tuple([h[x] for x in pos])] += [ln.strip()]
	
for h, listOfEntities in cluster.iteritems():
	print "%s:" % "".join(h)
	print "\n".join(listOfEntities)
	print
	
