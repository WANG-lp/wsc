
import progressbar

import os

import random
import collections

import sys
import cir

random.seed(1008)

class LSH:
	def __init__(self, b=10):
		self.baseVector = collections.defaultdict(dict)
		self.b          = b

	def _dotExpand(self, x, i):
		dot = 0.0
		
		for k, v in x.iteritems():
			if not self.baseVector[i].has_key(k):
				self.baseVector[i][k] = random.gauss(0, 1)

			dot += v * self.baseVector[i][k]

		return dot
	
	def hashing(self, data):
		ret = []
		
		for i in xrange(self.b):
			ret += ["1" if self._dotExpand(data, i) >= 0 else "0"]

		return ret

	def writeBaseVector(self, out):
		for k, bv in self.baseVector.iteritems():
			print k, bv
			
libcir = cir.test_cir_t("/work/naoya-i/kb/GoogleNews-vectors-negative300.bin", None, useMemoryMap=False)

def _getWord(x): return x.split(":")[0].split("-")[0]
def _insertVec(x, k, v):
	for i in xrange(len(v)):
		x[(k, i)] = v[i]
	
lsh				= LSH(b=int(sys.argv[2]))
pb				= progressbar.progressbar_t(int(os.popen("ls -l %s | cut -f5 -d' ' " % sys.argv[1]).read()))
bytesRead = 0

alreadict = {}

for ln in open(sys.argv[1]):
	pb.progress(len(ln))
	
	p1, p2, arg, sentdist, c1, c2, t1, t2, src = ln.split("\t")
	
	vec = {}

	# FOR PREDICATES
	# if not alreadict.has_key(_getWord(p1)):
	# 	alreadict[_getWord(p1)] = 1
	# 	vec = {}
	# 	_insertVec(vec, "p1", libcir.getWordVector(_getWord(p1)))

	for c, p in [(c1, p1), (c2, p2)]:
		if not alreadict.has_key(_getWord(p)+str(c)):
			alreadict[_getWord(p)+str(c)] = 1
			
			vec = {}
			drelCentroid = list(libcir.getWordVector(_getWord(p)))
			numSummed    = 1

			if 0 == len(drelCentroid): continue
			
			if "" != c:
				for drel in c.split(" "):
					try:
						t, e = drel.rsplit(":", 1)

						if "dobj" not in t and "iobj" not in t and "prep_" not in t and "subj" not in t: continue

						v = libcir.getWordVector(_getWord(e))
						
						for i in xrange(len(v)):
							drelCentroid[i] += v[i]

						numSummed += 1

					except ValueError:
						print >>sys.stderr, "Stuck in", ln

			for i in xrange(len(drelCentroid)):
				drelCentroid[i] /= numSummed

			_insertVec(vec, "ev", drelCentroid)

			print "\t".join([_getWord(p), c, "".join(lsh.hashing(vec))])

	# if not alreadict.has_key(_getWord(p2)):
	# 	alreadict[_getWord(p2)] = 1
	# 	vec = {}
	# 	_insertVec(vec, "p2", libcir.getWordVector(_getWord(p2)))
	# 	print "\t".join([_getWord(p2), "".join(lsh.hashing(vec))])
		
	# _insertVec(vec, "p1", libcir.getWordVector(_getWord(p1)))
	# _insertVec(vec, "p2", libcir.getWordVector(_getWord(p2)))
	# _insertVec(vec, "arg", libcir.getWordVector(_getWord(arg.split(",")[0])))

	# if "" != c1:
	# 	for drel in c1.split(" "):
	# 		try:
	# 			t, e = drel.rsplit(":", 1)
	# 			_insertVec(vec, "c1:%s" % t, libcir.getWordVector(_getWord(e)))

	# 		except ValueError:
	# 			print >>sys.stderr, "Stuck in", ln

	# if "" != c2:
	# 	for drel in c2.split(" "):
	# 		try:
	# 			t, e = drel.rsplit(":", 1)
	# 			_insertVec(vec, "c2:%s" % t, libcir.getWordVector(_getWord(e)))

	# 		except ValueError:
	# 			print >>sys.stderr, "Stuck in", ln
			
	# print "\t".join([ln.strip(), "".join(lsh.hashing(vec))]) #str(bytesRead), str(bytesRead+len(ln))])

	bytesRead += len(ln)

#lsh.writeBaseVector(sys.stdout)
