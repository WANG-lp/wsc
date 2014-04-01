
import re

import math
import struct
import collections
import mmap

import random
import cdb
import sys

# HELP: ARG: [WORD2VEC DB] [RULE DB] [P1:R1] [P2:R2] [INSTANCE OF ARG] [CONTEXT1] [CONTEXT2]
random.seed(777)

result_t = collections.namedtuple("result_t", "combinedScore simArgType simContext assoc instArg distSent context1 context2 source1 source2")

class test_cir_t:
	DIMENSION = 300
	
	def __init__(self, fnW2VF, fnRules, useMemoryMap = False):
		
		# READ THE WORD VECTOR INDEX.
		if None != fnW2VF:
			self.w2vi = dict([tuple(x.split("\t", 1)) for x in open(fnW2VF.replace(".bin", ".index.tsv"))]) if not useMemoryMap else cdb.init(fnW2VF.replace(".bin", ".index.cdb"))
			self.w2vf = open(fnW2VF, "rb")
			self.w2vdb = self.w2vf.read() if not useMemoryMap else mmap.mmap(self.w2vf.fileno(), 0, prot=mmap.PROT_READ)
			
		else:
			self.w2vdb = None
			
		# READ THE FREQUENCIES OF PREDICATES.
		if None != fnRules:
			self.totalFreqPreds = int(open(fnRules.replace("corefevents.tsv", "tuples.totalfreq.txt")).read())
			self.dbpreds = cdb.init(fnRules.replace("corefevents.tsv", "tuples.cdb"))
		
			# READ THE RULE INDEX.
			self.ri  = {}
			self.rf  = open(fnRules, "rb")
			self.rdb = self.rf.read() if not useMemoryMap else mmap.mmap(self.rf.fileno(), 0, prot=mmap.PROT_READ)

		else:
			self.rf = None
			
		self.cache_simargtype = {}

	def __del__(self):
		if None != self.rf:
			self.rf.close()

		if None != self.w2vdb:
			self.w2vf.close()
			
	def _getKey(self, k):
		return k[0].lower() if 'a' <= k[0].lower() and k[0].lower() <= "z" else "0"

	def _yieldEntry(self, db, idb, k, w2v=False):
		if w2v:			
			if isinstance(idb, dict):
				sampled = [idb[k]] if idb.has_key(k) else []
				
			else:
				sampled = idb.getall(k)
				
		else:
			if isinstance(idb, dict):
				kh = self._getKey(k)

				if not idb.has_key(kh):
					idb[kh] = cdb.init(self.rf.name.replace(".tsv", ".cdblist/corefevents.index.%s.cdb" % kh))

				sampled = idb[kh].getall(k)
			else:
				sampled = idb.getall(k)

		# random.shuffle(sampled)

		for index in sampled: #[:min(len(sampled), 3200)]:
			iStart, iLen = index.split("\t")
			yield len(sampled), db[int(iStart):int(iStart)+int(iLen)]

	def _getEntry(self, db, idb, k, w2v=False):
		return [x[1] for x in self._yieldEntry(db, idb, k, w2v)]
	
	def _getWordVector(self, ent):
		if None == self.w2vdb:
			return []
		
		binVec = self._getEntry(self.w2vdb, self.w2vi, ent, w2v=True)

		try:
			return struct.unpack("f"*test_cir_t.DIMENSION, binVec[0][len(ent)+1:]) if 0 < len(binVec) else []
		except struct.error:
			return []
		
	def _createContextualVector(self, c):
		v = collections.defaultdict(list)
		cnt = collections.defaultdict(int)

		for ce in c.split(" "):
			try:
				tp, rel, ent = ce.split(":")
			except ValueError:
				continue

			ent = ent.split("-")[0]

			for k, vec in enumerate(self._getWordVector(ent)):
				sig = ":".join([tp, rel])

				if not v.has_key(sig):
					v[sig] = [0.0] * test_cir_t.DIMENSION

				v[sig][k] += vec
				cnt[sig] += 1

		# TAKE THE AVERAGE.
		for sig, normalizer in cnt.iteritems():
			if 1 == normalizer: continue

			for i in xrange(test_cir_t.DIMENSION):
				v[sig][i] /= normalizer

		return v

	def _calcSimilarity(self, v1, v2):
		sim = 0.0
		toV1, toV2 = 0, 0

		if len(v1) != len(v2): return 0
		if 0 == len(v1):       return 0

		for i in xrange(len(v1)):
			sim += v1[i] * v2[i]
			toV1 += v1[i]**2
			toV2 += v2[i]**2

		sim /= math.sqrt(toV1)*math.sqrt(toV2)

		return 0.5*(1+sim)

	def _npmi(self, xy, x, y):
		return 0.5*(1+(math.log(1.0 * xy / (x * y), 2) / -math.log(xy, 2)))

	def _calcContextualSimilarity(self, ci, cj):
		if 0 == len(ci.keys()): return 0.0
								
		sim = 0
		#weights = {"dobj": 1.0, "iobj": 1.0, "nsubj": 1.0, "nsubjpass": 1.0, "advcl": 1.0}
		
		for k in set(ci.keys()) & set(cj.keys()):
			#print "  ", k, weights.get(k.split(":")[1], 0.2) * self._calcSimilarity(ci[k], cj[k])
			#sim += weights.get(k.split(":")[1], 0.2) * self._calcSimilarity(ci[k], cj[k])
			sim += self._calcSimilarity(ci[k], cj[k])
			
		return sim / len(ci.keys())

	def calcContextualSimilarity(self, c1, c2):
		vC1, vC2 = self._createContextualVector(c1), self._createContextualVector(c2)
		return self._calcContextualSimilarity(vC1, vC2)

	def getWordVector(self, w): return self._getWordVector(w)
		
	def calcSlotSimilarity(self, s1, s2):
		vS1, vS2 = self._getWordVector(s1), self._getWordVector(s2)
		return self._calcSimilarity(vS1, vS2)
		
	def getScores(self, p1, p2, filler = None):
		def _cdbdefget(f, key, de):
			r = f.get(key)
			return r if None != r else de

		pr1, pr2	 = p1[0], p2[0]
		myc1, myc2 = p1[1], p2[1]

		if pr1 > pr2:
			pr1, pr2 = pr2, pr1
			myc1, myc2 = myc2, myc1

		mycv1, mycv2 = self._createContextualVector(myc1.replace(",", " ")), self._createContextualVector(myc2.replace(",", " "))

		if None != filler:
			vFiller = self._getWordVector(filler)

		for itr in [self._yieldEntry(self.rdb, self.ri, "%s,%s" % (pr1, pr2)), self._yieldEntry(self.rdb, self.ri, "%s,%s" % (pr2, pr1))]:
			for numInst, ln in itr:
				ig1, ig2, _tp, sentdist, c1, c2, ig3, ig4, ig5 = ln.split("\t")

				for tp in _tp.split(","):
					vArgType = self._getWordVector(tp.split("-")[0])

					# CALCULATE THE CONTEXTUAL SIMILARITY.
					cv1, cv2	 = self._createContextualVector(c1), self._createContextualVector(c2)
					simArgType = (self._calcSimilarity(vFiller, vArgType) if not self.cache_simargtype.has_key((filler, tp)) else self.cache_simargtype[(filler, tp)]) \
							if None != filler else 0.0
					simContext = self._calcContextualSimilarity(mycv1, cv1) * self._calcContextualSimilarity(mycv2, cv2)
					#simContext = self._calcContextualSimilarity(mycv1, cv1) * self._calcContextualSimilarity(mycv2, cv2)

					self.cache_simargtype[(filler, tp)] = simArgType

					yield result_t(simArgType * simContext,
									simArgType, simContext,
									self._npmi(1.0*numInst / self.totalFreqPreds,
											 1.0*int(_cdbdefget(self.dbpreds, pr1, 0)) / self.totalFreqPreds,
											 1.0*int(_cdbdefget(self.dbpreds, pr2, 0)) / self.totalFreqPreds),
									tp, sentdist, c1, c2, ig3, ig4)
			
	
def main(args):	
	cir	 = test_cir_t(args[1], args[2], useMemoryMap=True)
	sim	 = 0
	Z    = 0
	
	for ret in cir.getScores( (args[3], args[6]), (args[4], args[7]), filler=args[5].split("-")[0] ):
		print "\t".join([repr(x) for x in [ret.combinedScore, ret.simArgType, ret.simContext, ret.instArg, ret.distSent, ret.context1, ret.context2, ret.source1, ret.source2]])

		sim += ret.combinedScore
		Z   += ret.simArgType + ret.simContext

	print 9999, sim / Z
	
if "__main__" == __name__: main(sys.argv)
