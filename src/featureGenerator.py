
import iri
import cir as conir

import stanfordHelper as scn

import sys
import itertools
import re
import collections
import math
import os
import cdb

#
def _isPredicate(x):  return x in "VB|VBD|VBG|VBN|VBP|VBZ|JJ|JJR|JJS".split("|")
def _isNounPhrase(x): return x in "NN|NNP|NNS|NNPS".split("|")

def _cdbdefget(f, key, de):
	r = f.get(key)
	return r if None != r else de

def _npmi(_xy, _x, _y):
	if 0 == _x*_y or 0 == _xy: return 0
	
	#return _xy/(_x*_y)
	return 0.5*(1+(math.log(1.0 * _xy / (_x * _y), 2) / -math.log(_xy, 2)))

class ranker_t:
	def __init__(self, ff, ana, candidates, sent):
		self.NN = collections.defaultdict(list)
		self.rankingsRv = collections.defaultdict(list)
		self.statistics = collections.defaultdict(list)

		# FOR REAL-VALUED FEATURES, WE FIRST CALCULATE THE RANKING VALUES
		# FOR EACH CANDIDATE.
		
		for can in candidates:
			wPrn, wCan	 = scn.getLemma(ana), scn.getLemma(can)
			vCan				 = can.attrib["id"]
			gvAna, gvCan = scn.getPrimaryPredicativeGovernor(sent, ana), scn.getPrimaryPredicativeGovernor(sent, can)
			
			self.rankingsRv["position"] += [(vCan, -int(can.attrib["id"]))]

			if None != gvAna and None != gvCan:
				r1 = ff.selPref("%s-%s" % (scn.getLemma(gvAna.token), gvAna.POS[0].lower()), gvAna.rel, "%s-n-%s" % (scn.getLemma(can), scn.getNEtype(can)))
				self.rankingsRv["nc"] += [(vCan, ff.nc(gvAna.lemma, gvAna.rel, gvCan.lemma, gvCan.rel))]
				self.rankingsRv["selpref"] += [(vCan, r1[1])]
				self.rankingsRv["selprefcnt"] += [(vCan, math.log(max(1, r1[0])))]

				r1 = ff.iri(self.NN,
										vCan,
										gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn,
										gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan,
										self.statistics["iriInstances"],
										)
				
				# r1 = ff.cir(self.NN, vCan, gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token),
				# 	    gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan,
				# 	    self.statistics["cirInstances"],
				# 	    )
				# self.statistics["cirNumRules"] += [(vCan, r1[5])]
				# self.statistics["cirComXY"] += [(vCan, r1[4][0])]
				# self.statistics["cirComX"] += [(vCan, r1[4][1])]
				# self.statistics["cirComY"] += [(vCan, r1[4][2])]
				
 				# self.rankingsRv["cirPMIMatch"] += [(vCan, r1[0])]
				
# 				self.rankingsRv["cirArgMatch"] += [(vCan, r1[1])]
# 				self.rankingsRv["cirConMatch"] += [(vCan, r1[2])]

# 				self.rankingsRv["cirArgConMatch"] += [(vCan, r1[1]+r1[2])]
# 				self.rankingsRv["cirConPMIMatch"] += [(vCan, r1[2]+r1[0])]
# 				self.rankingsRv["cirPMIArgMatch"] += [(vCan, r1[0]+r1[1])]
# 				self.rankingsRv["cirAllMatch"] += [(vCan, r1[0]+r1[1]+r1[2])]
				
# 				self.rankingsRv["cirComMatch"] += [(vCan, r1[3])]


				
				#self.rankingsRv["pk"] += [(vCan, ff.pk(gvAna.lemma, gvAna.rel, gvCan.lemma, gvCan.rel))]

				# r1 = ff.langmodel3("%s %s" % (wCan, gvAna.lemma) if "nsubj" == gvAna.rel else ("%s %s" % (gvAna.lemma, wCan)))
				# r2 = ff.langmodel3("%s %ss" % (wCan, gvAna.lemma) if "nsubj" == gvAna.rel else ("%ss %s" % (gvAna.lemma, wCan)))
				# r3 = ff.langmodel3("%s %ses" % (wCan, gvAna.lemma) if "nsubj" == gvAna.rel else ("%ses %s" % (gvAna.lemma, wCan)))
				# r4 = ff.langmodel3("%s %s" % (wCan, gvAna.lemma.replace("y", "ies")) if "nsubj" == gvAna.rel else ("%s %s" % (gvAna.lemma.replace("y", "ies"), wCan)))
				# self.rankingsRv["googleBI"] += [(vCan, max(r1[1], r2[1], r3[1], r4[1]))]
				# self.rankingsRv["googleBIcnt"] += [(vCan, math.log(max(1, r1[0], r2[0], r3[0], r4[0])))]

				# r1 = ff.langmodel3("%s %s %s" % (wCan, gvAna.lemma, scn.getLemma(gvAna.token.getnext())) if "nsubj" == gvAna.rel else ("%s %s %s" % (gvAna.lemma, scn.getLemma(gvAna.token.getnext()), wCan)))
				# r2 = ff.langmodel3("%s %ss %s" % (wCan, gvAna.lemma, scn.getLemma(gvAna.token.getnext())) if "nsubj" == gvAna.rel else ("%ss %s %s" % (gvAna.lemma, scn.getLemma(gvAna.token.getnext()), wCan)))
				# r3 = ff.langmodel3("%s %ses %s" % (wCan, gvAna.lemma, scn.getLemma(gvAna.token.getnext())) if "nsubj" == gvAna.rel else ("%ses %s %s" % (gvAna.lemma, scn.getLemma(gvAna.token.getnext()), wCan)))
				# r4 = ff.langmodel3("%s %s %s" % (wCan, gvAna.lemma.replace("y", "ies"), scn.getLemma(gvAna.token.getnext())) if "subj" == gvAna.rel else ("%s %s %s" % (gvAna.lemma.replace("y", "ies"), scn.getLemma(gvAna.token.getnext()), wCan)))
				# self.rankingsRv["googleTRI"] += [(vCan, max(r1[1], r2[1], r3[1], r4[1]))]
				# self.rankingsRv["googleTRIcnt"] += [(vCan, math.log(max(1, r1[0], r2[0], r3[0], r4[0])))]

				# r1 = ff.langmodel3("%s %s" % (gvAna.lemma, wCan)) if "JJ" in gvAna.POS else [0, 0]
				# self.rankingsRv["googleJC"] += [(vCan, r1[1])]
				# self.rankingsRv["googleJCcnt"] += [(vCan, math.log(max(1, r1[0])))]

		for rank in self.rankingsRv.values():
			rank.sort(key=lambda x: x[1], reverse=True)

	def getRankValue(self, x, t, de = 0.0, src = None):
		for xc in src[t] if None != src else self.rankingsRv[t]:
			if x == xc[0]: return xc[1]
			
		return de
		
	def getRank(self, x, t):
		if 1 >= len(self.rankingsRv[t]) or self.rankingsRv[t][0][1] == self.rankingsRv[t][1][1]:
			return None

		for i, xc in enumerate(self.rankingsRv[t]):
			if x == xc[0]: return "R1" if 0 == i else "R2"
		
	def getKNNRank(self, x, t, K=20):
		votes = collections.defaultdict(int)
		Ksorted = sorted(self.NN[t], key=lambda y: y[1], reverse=True)[:K]

		for votedCan, votedScore in Ksorted:
			votes[votedCan] += votedScore

		if len(votes) >= 2 and votes.values()[0] == votes.values()[1]:
			return 0 if Ksorted[-1][0] != x else 1

		for i, xc in enumerate(sorted(votes.iteritems(), key=lambda y: y[1], reverse=True)):
			if x == xc[0]: return i

		return len(votes)
	
	def getKNNRankValue(self, x, t, K=20, score=False, de=0):
		votes = collections.defaultdict(int)

		for votedCan, votedScore in sorted(self.NN[t], key=lambda y: y[1], reverse=True)[:K]:
			votes[votedCan] += 1 if not score else votedScore

		for i, xc in enumerate(votes.iteritems()):
			if x == xc[0]: return xc[1]

		return de

# LOAD THE KEY-VALUE STORE.
class feature_function_t:
	def __init__(self, pa, dirExtKb):
		self.pa							 = pa

		self.libiri    = iri.iri_t(
			os.path.join(dirExtKb, "corefevents.com.tsv"),
			os.path.join(os.path.dirname(sys.argv[0]), "../bin"),
			dirExtKb,
			os.path.join(dirExtKb, "corefevents.com.lsh")
			)
		self.libcir    = conir.test_cir_t(
			os.path.join(dirExtKb, "GoogleNews-vectors-negative300.bin"),
			os.path.join(dirExtKb, "corefevents.tsv"), useMemoryMap=pa.quicktest)
		
		self.cdb_sp		 = cdb.init(os.path.join(dirExtKb, "tuples.cdb"))
		self.sp_tfq		 = int(open(os.path.join(dirExtKb, "tuples.totalfreq.txt")).read())
		self.cdb_nc		 = cdb.init(os.path.join(dirExtKb, "nc12_assoc_verbs_wr_def.cdb"))
		self.cdb_cache = {}

		# GOOGLE NGRAMS
		if os.path.exists(os.path.join("/work/naoya-i/ngrams/", "1gram.cdb")) and \
					os.path.exists(os.path.join("/work/naoya-i/ngrams/", "1gram.total")):
			self.cdb_1gram			 = cdb.init(os.path.join("/work/naoya-i/ngrams/", "1gram.cdb"))
			self.cdb_ngram       = {}
			self.lm_1gram_total	 = int(open(os.path.join("/work/naoya-i/ngrams/", "1gram.total")).read())
			self.lm_idx2				 = collections.defaultdict(list)
			self.lm_idx3				 = collections.defaultdict(list)

			for ln in open(os.path.join("/work/naoya-i/ngrams/2gm.idx")):
				fn, w1, w2 = ln.strip().split()
				self.lm_idx2[w1[0]] += [fn]

			for ln in open(os.path.join("/work/naoya-i/ngrams/3gm.idx")):
				fn, w1, w2, w3 = ln.strip().split()
				self.lm_idx3[w1[0]] += [fn]
			
		# WILSON'S SUBJECTIVITY LEXICON.
		self.subjlex = {}

		for ln in open(os.path.join(dirExtKb, "wilson05_subj/subjclueslen1-HLTEMNLP05.tff")):
			ln = re.findall("word1=([^ ]+).*?priorpolarity=([^ ]+)\n", ln)
			
			if 0 < len(ln):
				self.subjlex[ln[0][0]] = ln[0][1]

		# CHAMBERS & JURAFSKY'S ORDERED VERB PAIRS.
		self.verbOrder = {}
		
		for ln in open(os.path.join(dirExtKb, "verb-pair-orders")):
			v1, v2, freq = ln.strip().split("\t")
			self.verbOrder[(v1, v2)] = int(freq)
		

	def generateFeature(self, ana, can, sent, ranker):
		conn				 = scn.getConn(sent)
		position		 = ranker.getRank(can.attrib["id"], "position")
		gvAna, gvCan = scn.getPrimaryPredicativeGovernor(sent, ana), scn.getPrimaryPredicativeGovernor(sent, can)

		# kNN FEATURES.
		for fk, fnn in ranker.NN.iteritems():
			r = ranker.getKNNRank(can.attrib["id"], fk)
			yield "%s_KNN_%s_%s" % (position, fk, r), 1
			
		# RANKING FEATURES.
		for fk, fr in ranker.rankingsRv.iteritems():
			if "position" == fk: continue
			
			r		 = ranker.getRank(can.attrib["id"], fk)
			diff = 0
			
			# if "cirPMI" in fk:
			# 	if 2 == len(ranker.rankingsRv[fk]):
			# 		myScore, oppScore = ranker.rankingsRv[fk][0 if "R1" == r else 1][1], ranker.rankingsRv[fk][1 if "R1" == r else 0][1]
			# 		diff              = int(10*abs(myScore-oppScore)/2.0)
			# 	else:
			# 		diff              = 10
					
			if None != r:
				yield "%s_%s_%s_%s" % (position, fk, r, diff), 1

			# if None != r:
			# 	yield "%s_%s" % (position, fk), fr[0 if "R1" == r else 1][1]
			
		# LEXICAL FEATURES.
		for tk in sent.xpath("./tokens/token"):
			yield "%s_L_%s" % (position, scn.getLemma(tk)), 1

			if None != conn:
				for tk2 in sent.xpath("./tokens/token"):
					if int(tk.attrib["id"]) < int(conn.attrib["id"]) and int(tk2.attrib["id"]) > int(conn.attrib["id"]) and \
								("VB" in scn.getPOS(tk) or "JJ" in scn.getPOS(tk)) and \
								("VB" in scn.getPOS(tk2) or "JJ" in scn.getPOS(tk2)):
						yield "%s_VPA_%s,%s" % (position, scn.getLemma(tk), scn.getLemma(tk2)), 1

		yield "%s_LL_%s,%s" % (position, scn.getLemma(ana), scn.getLemma(can)), 1

		if None != gvAna:
			yield "%s_PC_%s,%s" % (position, gvAna.lemma, scn.getLemma(can)), 1

			if None != gvCan:
				yield "%s_PP_%s,%s" % (position, gvAna.lemma, gvCan.lemma), 1
				
		  #yield ("%s_PRPR_%s-%s,%s-%s" % (position, gvAna.lemma, gvAna.rel, gvCan.lemma, gvCan.rel), 1)

		if "O" != scn.getNEtype(can):
			yield "%s_NE_%s,%s" % (position, scn.getLemma(ana), scn.getNEtype(can)), 1

	def _cdbgetc(self, db, k, de = None):
		gk = "%s-%s" % (db, k)
		
		if not self.cdb_cache.has_key(gk):
			self.cdb_cache[gk] = _cdbdefget(db, k, de)
			
		return self.cdb_cache[gk]

	def selPref(self, p, r, a):
		if None == self.cdb_sp:
			return (0, 0)

		freq_slot	 = int(self._cdbgetc(self.cdb_sp, "%s:%s" % (p, r), 1))
		freq_inst	 = int(self._cdbgetc(self.cdb_sp, "%s" % a, 1))
		freq_cooc	 = int(self._cdbgetc(self.cdb_sp, "%s:%s,%s" % (p, r, a), 1))
		freq_total = self.sp_tfq

		if 1 == freq_slot or 1 == freq_inst:
			return (0, 0)

		d    = (1.0 * freq_cooc / (freq_cooc+1)) * (1.0 * min(freq_slot, freq_inst) / (min(freq_slot, freq_inst)+1))
		npmi = _npmi(1.0*freq_cooc/freq_total, 1.0*freq_slot/freq_total, 1.0*freq_inst/freq_total)
		
		return (freq_cooc, npmi)
	
	def nc(self, p1, r1, p2, r2):
		q1 = ("X %s" if "nsubj" == r1 else "%s X") % p1
		q2 = ("X %s" if "nsubj" == r2 else "%s X") % p2
		r  = self._cdbgetc(self.cdb_nc, "%s ~ %s" % (q1, q2))
		
		return float(r) if None != r else 0.0

	def iri(self, outNN, NNvoted, p1, r1, ps1, c1, a1, p2, r2, ps2, c2, a2, cached = None):
		for ret, raw in self.libiri.predict(p1, "", r1, a1, p2, "", r2, a2, threshold = 1):
			if None != cached: cached += [(NNvoted, ret)]

			sp = ret.sIndexSlot[ret.iIndexed]*ret.sPredictedSlot*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred
			spa = sp * ret.sIndexArg[ret.iIndexed]*ret.sPredictedArg
			spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext

			assert(abs(spac - ret.score) < 0.1)
			
			outNN["iriPred"] += [(NNvoted, sp)]
			outNN["iriPredArg"] += [(NNvoted, spa)]
			
		for ret, raw in self.libiri.predict(p1, c1, r1, a1, p2, c2, r2, a2, threshold = 1):
			if None != cached: cached += [(NNvoted, ret)]

			sp = ret.sIndexSlot[ret.iIndexed]*ret.sPredictedSlot*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred
			spa = sp * ret.sIndexArg[ret.iIndexed]*ret.sPredictedArg
			spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext

			assert(abs(spac - ret.score) < 0.1)
			
			outNN["iriPredArgCon"] += [(NNvoted, spac)]

		return 0
						 
	def cir(self, outNN, NNvoted, p1, r1, ps1, c1, p2, r2, ps2, c2, filler, cached = None):
		voters	 = collections.defaultdict(list)
		comXY, comX, comY = 0.0, 0.0, 0.0

		for ret in self.libcir.getScores(
			("%s-%s:%s" %(p1, ps1[0].lower(), r1), c1),
			("%s-%s:%s" %(p2, ps2[0].lower(), r2), c2), filler):
		
			if None != cached: cached += [(NNvoted, ret)]

			outNN["cirArgPMI"] += [(NNvoted, ret.simArgType*ret.assoc)]
			outNN["cirPMICon"] += [(NNvoted, ret.assoc*ret.simContext)]
			outNN["cirArgConPMI"] += [(NNvoted, ret.simArgType*ret.simContext*ret.assoc)]
			voters["argconmatch"] += [ret.simArgType*ret.simContext]
			voters["argmatch"] += [ret.simArgType]
			voters["conmatch"] += [ret.simContext]
			comXY += ret.simArgType*ret.simContext
			comX  += ret.simArgType
			comY  += ret.simContext

		# if 0 < len(voters["argmatch"]):
		# 	comXY, comX, comY = \
		# 			comXY / len(voters["argmatch"]), comX / len(voters["argmatch"]), comY / len(voters["argmatch"])
		
		# TAKE THE k_BEST SUM.
		def _bestSum(_voter, _k):
			_voter.sort(reverse=True)
			return sum(_voter[:min(_k, len(_voter))])
	

		k = 10

		return (0, 0, 0,
						 #0, (0, 0, 0),
						 0, (0, 0, 0),
						 len(voters["argmatch"])) if 0 == len(voters["argmatch"]) else \
						 (ret.assoc, _bestSum(voters["argmatch"], k), _bestSum(voters["conmatch"], k),
							#_npmi(comXY, comX, comY), (comXY, comX, comY),
							_npmi(_bestSum(voters["argconmatch"], k), _bestSum(voters["argmatch"], k), _bestSum(voters["conmatch"], k)),
							(_bestSum(voters["argconmatch"], k), _bestSum(voters["argmatch"], k), _bestSum(voters["conmatch"], k)),
							len(voters["argmatch"]))
	
	def langmodel3(self, words):
		matched_fns = []
		w1          = words.split(" ")[0]
		lm_idx			= self.lm_idx2

		if 3 == len(words.split(" ")):
		 	lm_idx = self.lm_idx3

		for k in sorted(lm_idx.keys()):
			if w1 >= k:
				matched_fns += k

		for k in matched_fns[-2:]:
			for fn in lm_idx[k]:
				fn_cdb = os.path.join("/work/naoya-i/ngrams", fn).replace(".gz", ".cdb").replace("gm", "gram")

				if not self.cdb_ngram.has_key(fn_cdb):
					self.cdb_ngram[fn_cdb] = cdb.init(fn_cdb)
					
				r = self._cdbgetc(self.cdb_ngram[fn_cdb], words)

				if None != r:
					denom				 = 1.0 / self.lm_1gram_total
					single_freqs = []

					for w in words.split(" "):
						freq = self._cdbgetc(self.cdb_1gram, w)
						if None == freq: continue

						denom *= int(freq)
						single_freqs += [int(freq)]

					denom *= 1.0 / self.lm_1gram_total
					d	     = (1.0 * float(r) / (float(r)+1)) * (1.0 * min(single_freqs) / (min(single_freqs)+1))
					
					return int(r), d * math.log(float(r) / denom, 2)

		return 0, -9999
	
