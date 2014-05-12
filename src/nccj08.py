
import collections

import sys
import itertools
import re

class nccj08_t:
	def __init__(self, db1, db2):
		self.db = collections.defaultdict(list)

		ncid = 0
		
		for ln in open(db1):
			if ln.startswith("["):
				m = re.search("\[ ([^]]+) \]", ln)

				for pr1, pr2 in itertools.combinations(m.groups()[0].split(" "), 2):
					self.db[(pr1, pr2) if pr1 < pr2 else (pr2, pr1)] += [ncid]

				ncid += 1

		# CHAMBERS & JURAFSKY'S ORDERED VERB PAIRS.
		self.verbOrder = {}
		
		for ln in open(db2):
			v1, v2, freq = ln.strip().split("\t")
			self.verbOrder[(v1, v2)] = int(freq)
				
	def createQuery(self, p, r):
		if "nsubj" == r:                          r = "s"
		elif r in ["nsubj_pass", "dobj", "iobj"]: r = "o"
		
		return "%s-%s" % (p, r)
		
	def getChains(self, pr1, pr2):
		return self.db.get((pr1, pr2) if pr1 < pr2 else (pr2, pr1), [])

	def getVerbPairOrder(self, v1, v2):
		return int(self.verbOrder.get((v1, v2), 0))
		
if "__main__" == __name__:
	nc = nc_cj08_t("/work/naoya-i/schemas-size12", "/work/naoya-i/kb/verb-pair-orders")
	print nc.hasCausality(sys.argv[1], sys.argv[2])
