
import os

import sys
import collections
import itertools

import cir

cluster			 = collections.defaultdict(list)
query_vector = os.popen("grep -E '^%s\t' %s | awk '{print $NF}'" % (sys.argv[2], sys.argv[1])).read().strip()
libcir			 = cir.test_cir_t("/work/naoya-i/kb/GoogleNews-vectors-negative300.bin", None, useMemoryMap=True)

#
# PORTED FROM: http://jhafranco.com/2012/02/12/hamming-distance/
def hamming2(x,y):
	if len(x) != len(y): return max(len(x), len(y))
	
	count, z = 0, int(x, 2) ^ int(y, 2)
	
	while z:
		count += 1
		z &= z-1 # magic!

	return count
									
if "" == query_vector:
	print >>sys.stderr, "QUERY VECTOR NOT FOUND."
	sys.exit()

query_vector = query_vector[:int(sys.argv[4])]

print query_vector

result = []

for ln in open(sys.argv[1]):
	try:
		# p1, p2, arg, sentdist, c1, c2, t1, t2, src, h = ln.strip().split("\t")
		
		con, h = ln.strip().rsplit("\t", 1)
		h      = h[:int(sys.argv[4])]

		hammingDist = hamming2(h, query_vector)

		if hammingDist <= int(sys.argv[3]):
			if "-c" in sys.argv:
				p, c = con.split("\t")
				pq, cq = sys.argv[2].split("\t")
				
				result += [(con, libcir.calcSlotSimilarity(p, pq) * libcir.calcContextualSimilarity(c, cq))]
				
			else:
				result += [(con, libcir.calcSlotSimilarity(con, sys.argv[2]))]
			
	except ValueError:
		continue

result.sort(key=lambda x: x[1], reverse=True)

print "\n".join(map(lambda x: "%f %s" % (x[1], x[0]), result))
