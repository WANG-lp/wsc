import sys
import itertools
import re

for ln in open(sys.argv[1]):
	if ln.startswith("["):
		m = re.search("\[ ([^]]+) \]", ln)

		for p1, p2 in itertools.combinations(m.groups()[0].split(" "), 2):
			print "%s ~ %s\t1" % (p1, p2)
			
